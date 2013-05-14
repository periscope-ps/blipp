import shlex
import dateutil.parser
import calendar
import re

class Probe:
    def __init__(self, config={}):
        self.logfile = open(config["logfile"])

    def get_data(self):
        lines = self.logfile.read()
        ret = []
        for line in lines:
            line = shlex.split(line)
            aret = {}
            for pair in line:
                pair = pair.partition("=")
                if pair[0] == "ts":
                    val = self.date_to_unix(pair[2])
                else:
                    val = self._numberize(pair[2])
                if val:
                    aret[pair[0]] = val
            ret.append(aret)
        return ret


    def _numberize(self, astr):
        ret = None
        try:
            ret = int(astr)
        except ValueError:
            pass
        if ret:
            return ret
        try:
            ret = float(astr)
        except ValueError:
            return None
        return ret


    def date_to_unix(self, datestr):
        unix_seconds = calendar.timegm(dateutil.parser.parse(datestr).utctimetuple())
        fraction = re.search("\.([0-9]{1,6})", datestr)
        if fraction:
            fraction = fraction.group(1)
            while len(fraction) < 6:
                fraction += "0"
            fraction = int(fraction)
        unix_seconds *= 1000000
        unix_seconds += fraction
        return unix_seconds
