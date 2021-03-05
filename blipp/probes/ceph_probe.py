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
import subprocess
import json
from blipp.utils import full_event_types
from blipp import settings
from blipp.probes import abc

from unis.models import Service, Measurement

logger = settings.get_logger('ceph_probe')

EVENT_TYPES={
    "status":"ps:tools:blipp:linux:ceph:status",
    "used":"ps:tools:blipp:linux:ceph:bytes:used",
    "free":"ps:tools:blipp:linux:ceph:bytes:free"
}

class Probe(abc.Probe):
    command = ['ceph', '-s', '-f', 'json']

    def get_data(self):
        proc = subprocess.Popen(self.command,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        output = proc.communicate()

        if not output[0]:
            raise CmdError(output[1])
        try:
            data = self._extract_data(output[0])
        except ValueError as e:
            #logger.exc("get_data", e)
            return {}
        data = full_event_types(data, EVENT_TYPES)
        return data
        
    def _extract_data(self, stdout):
        json_output = json.loads(stdout)
        # {event_type: values}
        return {
                'status': json_output['health']['health']['health_services'][0]['mons'][0]['health'],
                'used': json_output['health']['health']['health_services'][0]['mons'][0]['kb_used'],
                'free': json_output['health']['health']['health_services'][0]['mons'][0]['kb_avail']
                }

class CmdError(Exception):
    def __init__(self, stderr):
        self.stderr = stderr

    def __str__(self):
        return "Exception in command line probe: " + self.stderr
