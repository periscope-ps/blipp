# =============================================================================
#  periscope-ps (blipp)
#
#  Copyright (c) 2013-2016, Trustees of Indiana University,
#  All rights reserved.
#
#  This software may be modified and distributed under the terms of the BSD
#  license.  See the COPYING file for details.
#
#  This software was created at the Indiana University Center for Research in
#  Extreme Scale Technologies (CREST).
# =============================================================================
import os
from .utils import full_event_types

class Proc:
    """Wrapper to opening files in /proc
    """
    def __init__(self, dirname="/proc"):
        """Initialize with optional alternate dirname.
        """
        self._dir = dirname

    def open(self, *path):
        """Open a given file under proc.
        'path' is a sequence of path components like ('net', 'dev')
        """
        return open(os.path.join(self._dir, *path))

EVENT_TYPES={
    'user':"ps:tools:blipp:linux:cpu:utilization:user",
    'system':"ps:tools:blipp:linux:cpu:utilization:system",
    'nice':"ps:tools:blipp:linux:cpu:utilization:nice",
    'iowait':"ps:tools:blipp:linux:cpu:utilization:iowait",
    'hwirq':"ps:tools:blipp:linux:cpu:utilization:hwirq",
    'swirq':"ps:tools:blipp:linux:cpu:utilization:swirq",
    'steal':"ps:tools:blipp:linux:cpu:utilization:steal",
    'guest':"ps:tools:blipp:linux:cpu:utilization:guest",
    'idle':"ps:tools:blipp:linux:cpu:utilization:idle",
    'onemin':"ps:tools:blipp:linux:cpu:load:onemin",
    'fivemin':"ps:tools:blipp:linux:cpu:load:fivemin",
    'fifteenmin':"ps:tools:blipp:linux:cpu:load:fifteenmin"
    }


class Probe:
    """Get processor/core statistics.

    Return scaled values instead of raw counters of jiffies.
    """
    CPU_TYPE = "socket"
    CORE_TYPE = "core"

    def __init__(self, service, measurement):
        self.config = measurement["configuration"]
        self._proc = Proc(self.config.get("proc_dir", "/proc/"))
        self._prev_cpu_hz = {}
        self._prev_cpu_total_hz = 0

    def get_data(self):
        """Get general host CPU information (first line of /proc/stat)

        Return: {'user':.1, 'system':.9, 'nice':0.0, etc... }
        """

        stat_file = self._proc.open("stat")
        line = stat_file.readline()
        #timestamp=time.time() # not sure whether this goes here or
                               # just before function call
        fields = line.split()
        key = fields[0]
        v = list(map(int, fields[1:]))

        # basic values
        cpudata = dict(list(zip(('user', 'nice', 'system', 'idle'), v[0:4])))
        # extended values
        if len(v) >= 7:
            cpudata.update(dict(list(zip(('iowait', 'hwirq', 'swirq'),
                                    v[4:7]))))
        # steal and guest if available
        if len(v) >=9:
            cpudata.update(dict(list(zip(('steal', 'guest'), v[7:9]))))
        # calculate deltas and scale
        prev_values = self._prev_cpu_hz
        prev_total = self._prev_cpu_total_hz
        total_hz = sum(v)
        total_elapsed_hz = total_hz - prev_total
        for key, value in list(cpudata.items()):
            prev = prev_values.get(key, 0.0)
            elapsed_hz = value - prev
            if total_elapsed_hz == 0:
                cpudata[key] = 0.0
            else:
                cpudata[key] = 1.0 * elapsed_hz / total_elapsed_hz
                prev_values[key] = value # save abs. value
        (d1, d2, d3) = os.getloadavg()
        cpudata.update({"onemin":d1, "fivemin":d2, "fifteenmin":d3})
        result=full_event_types(cpudata, EVENT_TYPES)
        self._prev_cpu_hz = prev_values
        self._prev_cpu_total_hz = total_hz
        return result

class CPUInfo:
    """Get processor/core statistics.

    Return scaled values instead of raw counters of jiffies.
    """
    CPU_TYPE = "socket"
    CORE_TYPE = "core"

    def __init__(self, proc=None, **_):
        self._proc = proc
        self._prev_cpu_hz = { }
        self._prev_cpu_total_hz = { }

    def get_data(self):
        """Get host CPU information.

        Return: list [ cpu  = list [ value, [ per-core-values.. ] ], ... ]
        """
        # Get system total from uptime. This will be used
        # to scale the CPU numbers to percentages.
        #f = open(os.path.join(self._dir, "uptime"), "r")
        #up_total, up_idle = map(float, f.readline().split())
        #total_elapsed = up_total - self._prev_up_total
        #if total_elapsed == 0: # not enough time has passed
        #    return self._prev_cpudata
        #self._prev_up_total = up_total
        # Get stat
        result, cpu = [ ], -1
        stat_file = self._proc.open("stat")
        for line in stat_file:
            fields = line.split()
            key = fields[0]
            v = list(map(int, fields[1:]))
            # cpu
            if key.startswith('cpu'):
                if key == 'cpu':
                    # new cpu
                    result.append([ { }, [ ] ])
                    cpu = len(result) - 1
                    core = -1
                else:
                    core = int(key[3:])
                idx = (cpu, core)
                # basic values
                cpudata = dict(list(zip(('user', 'nice', 'system', 'idle'), v[0:4])))
                # extended values
                if len(v) >= 7:
                    cpudata.update(dict(list(zip(('iowait', 'hwirq', 'swirq'),
                                            v[4:7]))))
                # steal and guest if available
                if len(v) >=9:
                    cpudata.update(dict(list(zip(('steal', 'guest'), v[7:9]))))
                # calculate deltas and scale
                prev_values = self._prev_cpu_hz.get(idx, {})
                prev_total = self._prev_cpu_total_hz.get(idx, 0.0)
                total_hz = sum(v)
                total_elapsed_hz = total_hz - prev_total
                for key, value in list(cpudata.items()):
                    prev = prev_values.get(key, 0.0)
                    elapsed_hz = value - prev
                    if total_elapsed_hz == 0:
                        cpudata[key] = 0.0
                    else:
                        cpudata[key] = 1.0 * elapsed_hz / total_elapsed_hz
                    prev_values[key] = value # save abs. value
                if core == -1:
                    result[cpu][0] = cpudata
                else:
                    # don't assume cores come in order; expand list
                    while len(result[cpu][1]) <= core:
                        result[cpu][1].append({})
                    result[cpu][1][core] = cpudata
                self._prev_cpu_hz[idx] = prev_values
                self._prev_cpu_total_hz[idx] = total_hz
        return result
