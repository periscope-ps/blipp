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
import resource
import os
from utils import full_event_types

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

    def exists(self, *path):
        try:
            a = open(os.path.join(self._dir, *path))
            return a
        except IOError:
            return False

EVENT_TYPES={
    "free":"ps:tools:blipp:linux:memory:utilization:free",
    "used":"ps:tools:blipp:linux:memory:utilization:used",
    "buffer":"ps:tools:blipp:linux:memory:utilization:buffer",
    "cache":"ps:tools:blipp:linux:memory:utilization:cache",
    "kernel":"ps:tools:blipp:linux:memory:utilization:kernel"
    }

class Probe:
    """Get memory statistics.
    """
    def __init__(self, service, measurement):
        self.service = service
        self.measurement = measurement
        self.config = measurement["configuration"]
        self._proc = Proc(self.config.get("proc_dir", "/proc/"))

    def get_data(self):
        bean_counts = self._proc.exists("user_beancounters")
        meminfo = self._proc.open("meminfo")
        ans = {}
        page_size_kb=resource.getpagesize()/1024
        total = 0
        free = 0
        for line in meminfo.readlines():
            linel=line.split()
            if not linel:
                continue
            if linel[0].startswith("MemFree"):
                ans.update({"free":int(linel[1])})
                free=int(linel[1])
            elif linel[0].startswith("Buffers"):
                ans.update({"buffer":int(linel[1])})
            elif linel[0].startswith("Cached"):
                ans.update({"cache":int(linel[1])})
            elif linel[0].startswith("MemTotal"):
                total=int(linel[1])
            elif linel[0].startswith("Slab"):
                ans.update({"kernel":int(linel[1])})
        ans.update({"used":(total-free)})

        if bean_counts: # we are on a vm
            del ans["kernel"]
            del ans["cache"]
            del ans["buffer"]
            # don't delete free - turns out its pretty tough to get a notion of free
            # in an openvz container, so we'll report free for the whole machine
            for line in bean_counts:
                linel=line.split()
                if "kmemsize" in linel:
                    loc = linel.index("kmemsize")+1
                    ans.update({"kernel":int(linel[loc])/1024})
                elif "physpages" in linel:
                    loc = linel.index("physpages")+1
                    ans.update({"used":int(linel[loc])*page_size_kb})

        ans = full_event_types(ans, EVENT_TYPES)
        return ans
