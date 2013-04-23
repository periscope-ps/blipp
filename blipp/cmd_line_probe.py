import subprocess
import re
from utils import full_event_types
import shlex
import settings

logger = settings.get_logger('cmd_line_probe')

class Probe:

    def __init__(self, config={}):
        self.config = config
        self.command = self._substitute_command(str(config.get("command")), self.config)
        self.data_regex = re.compile(str(config["regex"]))
        self.EVENT_TYPES = config["eventTypes"]

    def get_data(self):
        proc = subprocess.Popen(self.command,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        output = proc.communicate()

        if not output[0]:
            raise CmdError(output[1])
        data = self._extract_data(output[0])
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
        '''
        command = shlex.split(command)
        ret = []
        for item in command:
            if item[0] == '$':
                if item[1:].lower() in config:
                    sub = config[item[1:].lower()]
                    item = sub
            if item:
                ret.append(str(item))
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
