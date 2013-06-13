import resource
import os
import math
import sys
import ethtool
import socket
from unis_client import UNISInstance
import settings
from utils import full_event_types, blipp_import_method
import subprocess

class Proc:

    def __init__(self, dirname="/proc"):
        self._dir = dirname

    def open(self, *path):
        return open(os.path.join(self._dir, *path))


EVENT_TYPES={
    "write":"ps:tools:blipp:linux:disk:partition:write",
    "read":"ps:tools:blipp:linux:disk:partition:read"
}

class Probe:

    def __init__(self, config={}):
        self.config = config
        kwargs = config.get("kwargs", {})
        self._proc = Proc(kwargs.get("proc_dir", "/proc/"))
        self.unis = None

    def _get_unis(self):
        if not self.unis:
            self.unis = UNISInstance(self.config)
        return self.unis

    def partition_info(self, partition={}):
        hostName = socket.gethostname()
        hostRef = self._get_unis().get_node()
        hostRef = hostRef['selfRef']
        result = {}
        result['properties'] = {}
        result['name'] = "%s %s" % (hostName, partition['dev']) #node name
        result['host'] = hostRef #reference to system disk is on

        try: #check for uuid and add to properties
            line = subprocess.check_output("ls -l /dev/disk/by-uuid | grep %s" %partition['dev'], shell=True)
            split = line.split()
            result['properties']['uuid'] = split[8]
            result['properties']['path'] = "/dev/"+partition['dev']
        except:
            pass
        
        return result

    def parse_diskstats(self, dev=None):
        #columns of /proc/diskstats
        columns = ['m', 'mm', 'dev', 'reads', 'reads_merged', 'sectors_read',
                  'ms_reading', 'writes', 'writes_merged', 'sectors_written', 
                  'ms_writing', 'ios_in_progress', 'ms_io', 'weighted_ms_io']

        stat_file = self._proc.open("diskstats")
        result = {}

        lines = stat_file.readlines()
        
        for line in lines:
            if line == '': continue
            split = line.split()
            
            data = dict(zip(columns, split))
            if dev != None and dev != data['dev']:
                continue
            for key in data:
                if key != 'dev':
                    data[key] = int(data[key])

            result[data['dev']] = data

        return result 

    def calc_reads(self, drive):
        numReads = float(drive['reads'])
        readTime = float(drive['ms_reading'])
        if numReads != 0 and readTime != 0:
            readAvg = round(readTime/numReads)
        else:
            readAvg = 0
        return readAvg

    def calc_writes(self, drive):
        numWrites = float(drive['writes'])
        writeTime = float(drive['ms_writing'])
        if numWrites != 0 and writeTime != 0:
            writeAvg = round(writeTime/numWrites)
        else:
            writeAvg = 0
        return writeAvg

    def get_data(self):
        data = {}
        result = {}
        thisPartition = {}
        dataSet = self.parse_diskstats()
        f = open('./tempFile.txt', 'r+')
        partitions = {}

        test = self._get_unis()
        for key in dataSet:
            if key[0:2] == 'sd' and len(key) > 3:
                partitions[key] = dataSet[key]
        
        for key in partitions:
            thisPartition = self.partition_info(partitions[key])
            ref = self._find_or_post_node(thisPartition)
            data['write'] = self.calc_writes(partitions[key])
            data['read'] = self.calc_reads(partitions[key])
            newKey = ref['selfRef']
                
            result[newKey] = full_event_types(data, EVENT_TYPES)

        return result

    def _find_or_post_node(self, partition={}):
        f = open('./tempFile.txt', 'r+')
        exists = False

        nodeList = self._get_unis().get('nodes', [])
        for node in nodeList:
            if node['name'] == partition['name']:
                ref = node
                exists = True

        if not exists:
            ref = self.unis.post("/nodes", partition)

        return ref


