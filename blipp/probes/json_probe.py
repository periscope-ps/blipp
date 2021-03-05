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
from blipp import settings
from blipp.utils import full_event_types
from blipp.probes import abc

import shlex

logger = settings.get_logger('cmd_line_probe')

class Probe(abc.Probe):
    '''
    this is meant to be used by iperf3 specifically
    '''

    def __init__(self, service, measurement):
        super().__init__(service, measurement)
        self.command = self._substitute_command(str(self.config.command), self.config)
        try:
            self.EVENT_TYPES = self.config.eventTypes
        except Exception:
            self.EVENT_TYPES = {}

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
        
        throughput = 0
        interval_num = 0
        for interval in data['intervals']:
            throughput += interval['sum']['bits_per_second']
            interval_num += 1
            
        return {"ps:tools:blipp:linux:net:iperf:bandwidth": throughput / interval_num}

    def _extract_data(self, stdout):
        json_begin = stdout.index("Server JSON output:") + len("Server JSON output:")
        json_end = stdout.index("iperf Done.")
        json_output = json.loads(stdout[json_begin:json_end])
        return json_output
        '''
        matches = self.data_regex.search(stdout)
        if not matches:
            raise NonMatchingOutputError(stdout)
        return matches.groupdict()
        '''
        

    def _substitute_command(self, command, config):
        ''' command in form "ping $ADDRESS"
        config should have substitutions like "address": "example.com"
        Note; now more complex
        '''
        command = shlex.split(command)
        ret = []
        for item in command:
            if item[0] == '$':
                if hasattr(config, item[1:]):
                    val = getattr(config, item[1:])
                    if isinstance(val, bool):
                        if val:
                            ret.append(item[1:])
                    elif item[1]=="-":
                        ret.append(item[1:])
                        ret.append(str(val))
                    else:
                        ret.append(str(val))
            elif item:
                ret.append(item)
        #logger.info('substitute_command', cmd=ret, name=self.config['name'])
        logger.info(name=self.config.name)
        return ret


class NonMatchingOutputError(Exception):
    def __init__(self, output):
        self.output = output

    def __str__(self):
        return "output did not match regex... output: " + self.output


class CmdError(Exception):
    def __init__(self, stderr):
        self.stderr = stderr

    def __str__(self):
        return "Exception in command line probe: " + self.stderr
