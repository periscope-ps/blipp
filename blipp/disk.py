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
    "write":"ps:tools:blipp:linux:disk:utilization:write",
    "read":"ps:tools:blipp:linux:disk:utilization:read"
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
        result = {}
        result['properties'] = {}
        result['name'] = "%s %s" % (hostName, partition['dev'])
        lines = subprocess.check_output(["ls", "-l","/dev/disk/by-uuid"])
        lines = lines.splitlines()

        for line in lines:
            if line == '': continue
            line = line.rstrip('\r\n')
            if line[-4:] == partition['dev']:
                split = line.split()
                result['properties']['uuid'] = split[8]
                result['properties']['path'] = "/dev/"+partition['dev']
        
        return result

    def parse_diskstats(self, dev=None):
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

        return result #return dict entries for each device

    #def calc_reads(self, dataSet, driveType):
        #drive = dataSet[driveType]
    def calc_reads(self, drive):
        numReads = float(drive['reads'])
        readTime = float(drive['ms_reading'])
        if numReads != 0 and readTime != 0:
            readAvg = round(readTime/numReads)
        else:
            readAvg = 0
        return readAvg

    #def calc_writes(self, dataSet, driveType):
        #drive = dataSet[driveType]
    def calc_writes(self, drive):
        numWrites = float(drive['writes'])
        writeTime = float(drive['ms_writing'])
        if numWrites != 0 and writeTime != 0:
            writeAvg = round(writeTime/numWrites)
        else:
            writeAvg = 0
        return writeAvg

    def get_data(self):
        hereCount = 0
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
            #f.write(partitions[key]['dev'])
            thisPartition = self.partition_info(partitions[key])
            ref = self._find_or_post_node(thisPartition)
            hereCount += 1
            data['write'] = self.calc_writes(partitions[key])
            data['read'] = self.calc_reads(partitions[key])
            result[key] = full_event_types(data, EVENT_TYPES)
            #result[key]['selfRef'] = "test"
            #f.write("%s" %data)

        f.write("%s" %result)
        return result

    def _find_or_post_node(self, partition={}):
        #f = open('./tempFile.txt', 'r+')
        #sampleNode = {'name': 'testNode', 'other': 'othertest'}
        #sampleNode['properties'] = {}
        #sampleNode['properties']['path'] = "/dev/sda5"
        #postedNode = self.unis.post("/nodes", sampleNode)
        #f.write(postedNode["selfRef"])
        ref = self.unis.post("/nodes", partition)
        return ref


#myProbe = Probe()
#myProbe.get_data()
