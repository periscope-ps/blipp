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

    def _partition_info(self, partition={}):
        hostName = socket.gethostname()
        hostRef = self.unis.get(self.service["runningOn"]["href"])
        hostRef = hostRef['selfRef']
        result = {}
        result['properties'] = {}
        result['name'] = "%s %s" % (hostName, partition['dev']) #node name
        result['host'] = hostRef #reference to system disk is on

        try: #free space on mounted drives, likely just where root file system is mounted
            line = subprocess.check_output("df -h | grep %s" %partition['dev'], shell=True)
            split = line.split()
            result['properties']['free space'] = split[3]
        except:
            logger.info('free disk space', msg='free space info for %s is unavailable' %partition['dev'])

        try: #disk sizes
            line = subprocess.check_output("lsblk | grep %s" %partition['dev'], shell=True)
            split = line.split()
            result['properties']['size'] = split[3]
        except:
            logger.info('disk size', msg='unable to retrieve size of partition %s' %partition['dev'])
        
        try: #check for uuid and add to properties
            line = subprocess.check_output("ls -l /dev/disk/by-uuid | grep %s" %partition['dev'], shell=True)
            split = line.split()
            result['properties']['uuid'] = split[8]
        except:
            logger.info('uuid', msg='partition %s has no UUID' %partition['dev'])
        
        result['properties']['path'] = "/dev/"+partition['dev']

        return result

    def _parse_diskstats(self, dev=None):
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
        except:
            logger.warn('lsblk', msg="Unable to retrieve partition info from command 'lsblk'")
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
        result = {"write":"ps:tools:blipp:linux:disk:partition:%s:average:write:ms" %partition['dev'],
                  "read":"ps:tools:blipp:linux:disk:partition:%s:average:read:ms" %partition['dev'],
                  "weighted_io":"ps:tools:blipp:linux:disk:partition:%s:weighted:io:ms" %partition['dev']}
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
            data['write'] = self._calc_writes(partitions[key])
            data['read'] = self._calc_reads(partitions[key])
            data['weighted_io'] = partitions[key]['weighted_ms_io']
            newKey = ref['selfRef']
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
