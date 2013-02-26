import subprocess
import re
from utils import full_event_types
import shlex

class Probe:

    def __init__(self, config={}):
        self.config = config
        kwargs = config.get("kwargs", {})
        self.command = str(kwargs.get("command"))
        self.data_regex = re.compile(str(kwargs["regex"]))
        self.EVENT_TYPES = kwargs["eventTypes"]

    def get_data(self):
        proc = subprocess.Popen(shlex.split(self.command),
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
