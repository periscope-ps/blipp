import settings
import shlex
import dateutil.parser
import calendar
import re

logger = settings.get_logger("netlogger_probe")

class Probe:
    def __init__(self, service, measurement):
        self.config = measurement["configuration"]
        self.logfile = None
        try:
            self.logfile = open(self.config["logfile"])
        except KeyError:
            logger.warn("__init__", msg="Config does not specify logfile!")
        except IOError:
            logger.warn("__init__", msg="Could not open logfile: %s" % self.config["logfile"])

        self.app_name = self.config.get("appname", "")
        self.et_string = "ps:tools:blipp:netlogger:"
        if self.app_name:
            self.et_string += self.app_name + ":"

    def get_data(self):
        if self.logfile:
            ret = []
            self.logfile.seek(self.logfile.tell())
            for line in self.logfile:
                if "VAL" not in line:
                    self.parse_calipers(ret, line)
                else:
                    line = shlex.split(line)
                    for pair in line:
                        pair = pair.partition("=")
                        if pair[0] == "ts":
                            ts = self.date_to_unix(pair[2])
                        if pair[0] == "VAL":
                            val = self._numberize(pair[2])
                        if pair[0] == "event":
                            event = self.et_string + pair[2]

                    ret.append({"ts": ts, event: val})
            return ret
        else:
            logger.error("get_data", msg="No logfile available")

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
            unix_seconds += float(fraction)/10e5
        return unix_seconds

    def parse_calipers(self, ret, line):
        line = shlex.split(line)
        cal_events = []
        for pair in line:
            pair = pair.partition("=")
            if pair[0] == "ts":
                ts = self.date_to_unix(pair[2])
            elif pair[0] == "event":
                event = self.et_string + pair[2]
            else:
                cal_events.append({"e": event+":"+pair[0], "v": self._numberize(pair[2])})
        
        for ce in cal_events:
            ret.append({"ts": ts, ce['e']: ce['v']})
