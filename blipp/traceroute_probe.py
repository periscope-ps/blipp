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
import re
from .utils import full_event_types
import shlex
from . import settings

logger = settings.get_logger('traceroute_probe')

class Probe:

    def __init__(self, service, measurement):
        self.service = service
        self.measurement = measurement
        self.config = measurement["configuration"]
        self.command = self._substitute_command(str(self.config.get("command")), self.config)
        try:
            self.data_regex = re.compile(
                str(self.config["regex"]),
                flags=re.M)
        except Exception:
            self.data_regex = None
        try:
            self.EVENT_TYPES = self.config["eventTypes"]
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
        except NonMatchingOutputError as e:
            #logger.exc("get_data", e)
            return {}
        data = full_event_types(data, self.EVENT_TYPES)
        return data

    def _extract_data(self, stdout):
        matches = self.data_regex.finditer(stdout)
        if not matches:
            raise NonMatchingOutputError(stdout)
        ret = {'hopip': []}
        previous_hop = None
        hop_list = {}
        for m in matches:
            d = m.groupdict()
            current_hop = d['hop']
            if not previous_hop and not current_hop:
                continue
            elif not current_hop:
                current_hop = previous_hop

            hop_list.setdefault(current_hop, []).append(d['hopip'] and d['hopip'][1:-1] or '*')

            previous_hop = current_hop

        for i in range(len(hop_list)):
            ret['hopip'].append(hop_list[str(i + 1)])

        return ret
    
    def _substitute_command(self, command, config):
        command = shlex.split(command)
        ret = []
        for item in command:
            if item[0] == '$':
                if item[1:] in config:
                    val = config[item[1:]]
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
        logger.info(name=self.config['name'])
        
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
