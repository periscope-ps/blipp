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

logger = settings.get_logger('disk')

class Proc:

    def __init__(self, dirname="/proc"):
        self._dir = dirname

    def open(self, *path):
        return open(os.path.join(self._dir, *path))

class Probe:

    def __init__(self, service, measurement):
        self.service = service
        self.measurement = measurement
        self.config = measurement['configuration']
        kwargs = self.config.get("kwargs", {})
        self._proc = Proc(kwargs.get("proc_dir", "/proc/"))
        self.unis = UNISInstance(self.service)
        self.alt_version = False

    def _partition_info(self, partition={}):
        dev = partition['dev']
        hostName = socket.gethostname()
        hostRef = self.unis.get(self.service["runningOn"]["href"])
        hostRef = hostRef['selfRef']
        result = {}
        result['properties'] = {}
        result['name'] = "%s %s" % (hostName, dev) #node name
        result['host'] = hostRef #reference to system disk is on

        line = subprocess.check_output("lsblk | grep %s" %dev, shell=True)
        split = line.split()
        result['properties']['size'] = split[3]

        lines = subprocess.check_output("df -h", shell=True)
        if dev in lines:
            lines = lines.splitlines()
            for line in lines:
                if dev in line:
                    split = line.split()
                    result['properties']['free space'] = split[3]
        else:
            result['properties']['free space'] = 'unavailable'
        
        lines = subprocess.check_output("ls -l /dev/disk/by-uuid", shell=True)
        if dev in lines:
            lines = lines.splitlines()
            for line in lines:
                if dev in line:
                    split = line.split()
                    result['properties']['uuid'] = split[8]
        else:
            result['properties']['uuid'] = 'n/a'
        
        result['properties']['path'] = "/dev/"+dev

        return result

    def _parse_diskstats(self, dev=None):
        #columns of /proc/diskstats
        columns = ['m', 'mm', 'dev', 'reads', 'reads_merged', 'sectors_read',
                  'ms_reading', 'writes', 'writes_merged', 'sectors_written', 
                  'ms_writing', 'ios_in_progress', 'ms_io', 'weighted_ms_io']

        alt_columns = ['m', 'mm', 'dev', 'reads', 'sectors_read', 'writes', 'sectors_written'] #kernel 2.6.0 - 2.6.24

        stat_file = self._proc.open("diskstats")
        result = {}
        lines = stat_file.readlines()
        
        for line in lines:
            if line == '': continue
            split = line.split()
            if len(split) == 14:
                data = dict(zip(columns, split))
                if dev != None and dev != data['dev']:
                    continue
                for key in data:
                    if key != 'dev':
                        data[key] = int(data[key])

            elif len(split) == 7: #kernel 2.6.0 - 2.6.24
                data = dict(zip(alt_columns, split))
                self.alt_version = True
                if dev != None and dev != data['dev']:
                    continue
                for key in data:
                    if key != 'dev':
                        data[key] = int(data[key])

            result[data['dev']] = data

        return result 

    def _parse_lsblk(self):
        columns = ['name', 'dev_nums', 'rm', 'size', 'ro', 'type', 'mount_point']
        f = open('./tempFile.txt', 'r+')
        partList = []
        try:
            lines = subprocess.check_output('lsblk -l -n', shell=True)
            lines = lines.splitlines()
            for line in lines:
                split = line.split()
                parts = dict(zip(columns, split))
                for key in parts:
                    if key == 'type':
                        if parts['type'] == 'part':
                            partList.append(parts['name'])
        except Exception as e:
            logger.exc('_parse_lsblk', e)
        return partList

    def _calc_reads(self, drive):
        numReads = float(drive['reads'])
        readTime = float(drive['ms_reading'])
        if numReads != 0 and readTime != 0:
            readAvg = round(readTime/numReads)
        else:
            readAvg = 0
        return readAvg

    def _calc_writes(self, drive):
        numWrites = float(drive['writes'])
        writeTime = float(drive['ms_writing'])
        if numWrites != 0 and writeTime != 0:
            writeAvg = round(writeTime/numWrites)
        else:
            writeAvg = 0
        return writeAvg

    def _build_event_types(self, partition={}):
        dev = partition['dev']
        if not self.alt_version:
            result = {"read":"ps:tools:blipp:linux:disk:partition:%s:average:read:ms" %dev,
                      "write":"ps:tools:blipp:linux:disk:partition:%s:average:write:ms" %dev,
                      "weighted_io":"ps:tools:blipp:linux:disk:partition:%s:weighted:io:ms" %dev}
        else: #kernel 2.6.0 - 2.6.24
            result = {"reads":"ps:tools:blipp:linux:disk:partition:%s:reads:issued" %dev,
                      "sectors_read":"ps:tools:blipp:linux:disk:partition:%s:sectors:read" %dev,
                      "writes":"ps:tools:blipp:linux:disk:partition:%s:writes:issued" %dev,
                      "sectors_written":"ps:tools:blipp:linux:disk:partition:%s:sectors:written" %dev}
        return result

    def get_data(self):
        data = {}
        result = {}
        thisPartition = {}
        dataSet = self._parse_diskstats()
        partitions = {}
        partList = self._parse_lsblk() #get the names of all partitions
        
        for key in dataSet:
            if key in partList:
                partitions[key] = dataSet[key] #see if the item from diskstats is a partition

        for key in partitions: #get all data for each partition
            thisPartition = self._partition_info(partitions[key])
            ref = self._find_or_post_node(thisPartition)
            newKey = ref['selfRef']

            if not self.alt_version:
                data['read'] = self._calc_reads(partitions[key])
                data['write'] = self._calc_writes(partitions[key])
                data['weighted_io'] = partitions[key]['weighted_ms_io']
            else:
                data['reads'] = partitions[key]['reads']
                data['sectors_read'] = partitions[key]['sectors_read']
                data['writes'] = partitions[key]['writes']
                data['sectors_written'] = partitions[key]['sectors_written']
                
            eventTypes = self._build_event_types(partitions[key])
                
            result[newKey] = full_event_types(data, eventTypes)

        return result

    def _find_or_post_node(self, partition={}):
        exists = False

        nodeList = self.unis.get('nodes', [])
        for node in nodeList:
            if node['name'] == partition['name']:
                ref = node
                exists = True

        if not exists:
            ref = self.unis.post("/nodes", partition)

        return ref
