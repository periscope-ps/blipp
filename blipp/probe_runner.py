import settings
import time
from collector import Collector
from utils import blipp_import
import pprint

logger = settings.get_logger('probe_runner')

class ProbeRunner:
    '''
    Class to handle a single probe. Creates the scheduler, collector,
    and probe module associated with this probe. The run method should
    be called as a subprocess (by arbiter) and passed a
    connection object so that it can receive a "stop" if necessary.
    '''

    def __init__(self, service, measurement):
        self.measurement = measurement
        self.config = measurement['configuration']
        self.service = service.config
        self.probe_defaults = service.probe_defaults
        self.setup()

    def run(self, conn):
        for nextt in self.scheduler:
            logger.debug("run", msg="got time from scheduler", time=nextt)
            if conn.poll():
                if conn.recv() == "stop":
                    self._cleanup()
                    break
            time.sleep(max(nextt-time.time(), 0))
            self.collect()

    def collect(self):
        logger.debug('collect', name=self.config['name'], module=self.config["probe_module"])
        data = self.probe.get_data()
        ts = time.time()
        if data:
            if isinstance(data, list):
                for d in data:
                    self.collector.insert(self._normalize(d), ts)
            else:
                self.collector.insert(self._normalize(data), ts)

    def _normalize(self, data):
        if isinstance(data.itervalues().next(), dict):
            return data
        subject = self.service["runningOn"]["href"]
        return dict({subject: data})


    def setup(self):
        config = self.config
        logger.info('setup', name=config["name"], module=config["probe_module"], config=pprint.pformat(config))
        probe_mod = blipp_import(config["probe_module"])
        self.probe = probe_mod.Probe(self.service, self.measurement)

        if "." in config["collection_schedule"]:
            sched_file, sched_name = config["collection_schedule"].split('.')
        else:
            sched_file, sched_name = "builtins", config["collection_schedule"]

        logger.info('setup', sched_file=sched_file, sched_name=sched_name)
        self.scheduler = blipp_import("schedules." + sched_file, fromlist=[1]).__getattribute__(sched_name)
        self.scheduler = self.scheduler(self.service, self.measurement)
        self.collector = Collector(self.service, self.measurement)


    def _cleanup(self):
        '''
        Used for graceful exit. Clear any outstanding unreported data.
        '''
        logger.debug('_cleanup', name=self.config['name'])
        self.collector.report()
