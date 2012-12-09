import subprocess
import re
from utils import full_event_types

EVENT_TYPES={
    'rtt':"ps:tools:blipp:linux:net:ping:rtt",
    'ttl':"ps:tools:blipp:linux:net:ping:ttl"}

class Probe:

    def __init__(self, config={}):
        self.config = config
        kwargs = config.get("kwargs", {})
        if not kwargs.get("timeout", None) or kwargs["timeout"] <= 0:
            kwargs["timeout"] = 2
        if not kwargs.get("packetsize", None):
            kwargs["packetsize"] = 56
        self.timeout_arg="-W " + str(kwargs["timeout"])
        self.packetsize_arg="-s " + str(kwargs["packetsize"])
        self.count_arg="-c 1"
        self.address=kwargs.get("address", "localhost")

    def get_data(self):
        ping_proc = self._get_subprocess()
        output = ping_proc.communicate()
        #output is a tuple of (stdout, stderr)

        if not output[0]:
            raise PingError(output[1])
        data = self._extract_data(output[0])
        data = full_event_types(data, EVENT_TYPES)
        return data


    def _get_subprocess(self):
        return subprocess.Popen(["ping",
                                 self.timeout_arg,
                                 self.count_arg,
                                 self.address],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

    def _extract_data(self, stdout):
        ping_regex = re.compile(
            'ttl=(?P<ttl>\d+).*time=(?P<rtt>\d+\.\d+) (?P<units>[A-Za-z]+)')
        matches = ping_regex.search(stdout)
        if not matches:
            raise NonMatchingOutputError(stdout)
        gdict = matches.groupdict()
        units = gdict.pop('units')
        if units.lower() != "ms":
            raise UnknownUnitsError(units)
        return gdict


class NonMatchingOutputError(Exception):
    def __init__(self, output):
        self.output = output

    def __str__(self):
        return "ping output did not match regex... output: " + self.output


class UnknownUnitsError(Exception):
    def __init__(self, units):
        self.units = units

    def __str__(self):
        return "ping reported unkown rtt units: " + self.units


class PingError(Exception):
    def __init__(self, stderr):
        self.stderr = stderr

    def __str__(self):
        return "Exception in ping probe: " + output[1]
