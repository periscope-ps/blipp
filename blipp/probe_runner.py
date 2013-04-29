import settings
import time
from collector import Collector
from utils import blipp_import
import pprint

logger = settings.get_logger('probe_runner')

class ProbeRunner:
    def __init__(self, config):
        self.config = config
        self.setup()

    def run(self, conn):
        for nextt in self.scheduler:
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
            self.collector.insert(self._normalize(data), ts)

    def _normalize(self, data):
        if isinstance(data.itervalues().next(), dict):
            return data
        subject = self.config["runningOn"]["href"]
        return dict({subject: data})


    def setup(self):
        config = self.config
        logger.info('setup', name=config["name"], module=config["probe_module"], config=pprint.pformat(self.config))
        probe_mod = blipp_import(config["probe_module"])
        self.probe = probe_mod.Probe(config)

        if "." in config["collection_schedule"]:
            sched_file, sched_name = config["collection_schedule"].split('.')
        else:
            sched_file, sched_name = "builtins", config["collection_schedule"]
        logger.info('setup', sched_file=sched_file, sched_name=sched_name)
        self.scheduler = blipp_import("schedules." + sched_file, fromlist=[1]).__getattribute__(sched_name)
        self.scheduler = self.scheduler(config=config, **config["schedule_params"])

        self.collector = Collector(config)


    def _cleanup(self):
        logger.debug('_cleanup', name=self.config['name'])
        self.collector.report()
