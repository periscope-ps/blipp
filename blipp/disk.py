import resource
import os
import math
from utils import full_event_types

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

    def calc_reads(self, dataSet, driveType):
        drive = dataSet[driveType]
        numReads = float(drive['reads'])
        readTime = float(drive['ms_reading'])
        readAvg = round(readTime/numReads)
        return readAvg

    def calc_writes(self, dataSet, driveType):
        drive = dataSet[driveType]
        numWrites = float(drive['writes'])
        writeTime = float(drive['ms_writing'])
        writeAvg = round(writeTime/numWrites)
        return writeAvg

    def get_data(self):

        result = {}
        dataSet = self.parse_diskstats()

        for key in dataSet:
            if key[0:2] == 'sd' and len(key) == 3:
                thisKey = key[0:3]
                readString = thisKey + ' reads'
                writeString = thisKey + ' writes'
                result[readString] = self.calc_reads(dataSet, thisKey)
                result[writeString] = self.calc_writes(dataSet, thisKey)

            elif key[0:2] == 'hd' and len(key) == 3:
                thisKey = key[0:3]
                result[thisKey] = self.calc_reads(dataSet, thisKey)
                writeString = thisKey + ' writes'
                result[readString] = self.calc_reads(dataSet, thisKey)
                result[writeString] = self.calc_writes(dataSet, thisKey)

        return result

#myProbe = Probe()
#myProbe.get_data()
#myProbe.__init__()
#result = myProbe.get_data() #get the list of dict entries
#entry = result['sda'] #get the entry for sda
#print entry['ms_writing'] #print ms_writing
