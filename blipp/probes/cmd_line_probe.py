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
from blipp import settings
from blipp.utils import full_event_types
from blipp.probes import abc
import shlex

logger = settings.get_logger('cmd_line_probe')

class Probe(abc.Probe):
    def __init__(self, service, measurement):
        super().__init__(service, measurement)
        self.command = self._substitute_command(self.config.command, self.config)
        try:
            self.data_regex = re.compile(
                str(self.config.regex),
                flags=re.S|re.M)
        except Exception:
            self.data_regex = None
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
        except NonMatchingOutputError as e:
            #logger.exc("get_data", e)
            return {}
        data = full_event_types(data, self.EVENT_TYPES)
        return data

    def _extract_data(self, stdout):
        matches = self.data_regex.search(stdout)
        if not matches:
            raise NonMatchingOutputError(stdout)
        return matches.groupdict()

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
