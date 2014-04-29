import settings

logger = settings.get_logger('data_logger')

class DataLogger:
    def __init__(self, service_entry, measurement):
        self.service_entry = service_entry
        self.sconfig = service_entry["properties"]["configurations"]
        self.mconfig = measurement["configuration"]
        self.filepath=self.mconfig.get("data_file", None)
        if self.filepath:
            try:
                self.datafile = open(self.filepath, "a")
            except IOError:
                logger.warn("__init__", msg="Could not open datafile: %s" % self.filepath)
            
    def write_data(self, data, mid_to_et=None):
        if not self.filepath:
            return None
        for d in data:
            for i in d['data']:
                outstr = "ts=%s event=%s mid=%s value=%s\n" % (str(int(i['ts'])),
                                                               mid_to_et[d['mid']],
                                                               d['mid'],
                                                               str(i['value']))
                try:
                    self.datafile.write(outstr)
                    self.datafile.flush()
                except Exception as e:
                    logger.info("write_data", msg="Could not write to file: %s" % e)
        return data
