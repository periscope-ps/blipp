from ms_client import MSInstance
from unis_client import UNISInstance
import settings
logger = settings.get_logger('collector')
from utils import blipp_import


class Collector:
    """Collects reported measurements and aggregates them for
    sending to MS at appropriate intervals.

    Also does a bunch of other stuff which should probably be handled by separate classes.
    Creates all the metadata objects, and the measurement object in UNIS for all data inserted.
    Depends directly on the MS and UNIS... output could be far more modular.
    """

    def __init__(self, config):
        self.config = config
        self.collections_created = False
        self.ms = MSInstance(config)
        self.mids = {} # {subject1: {metric1:mid, metric2:mid}, subj2: {...}}
        # {mid: [{"ts": ts, "value": val}, {"ts": ts, "value": val}]}
        self.mid_to_data = {}
        self.unis = UNISInstance(config)
        self.num_collected = 0
        self._post_measurement()

    def insert(self, data, ts):
        '''
        Called (by probe_runner) to insert new data into this collector object.
        '''
        mids = self.mids
        for subject, met_val in data.iteritems():
            if "ts" in met_val:
                ts = met_val["ts"]
                del met_val["ts"]
            for metric, value in met_val.iteritems():
                if not metric in mids.get(subject, {}):
                    r = self.unis.post_metadata(subject, metric, self.measurement)
                    mids.setdefault(subject, {})[metric] = r["id"]
                    self.mid_to_data[r["id"]] = []
                self._insert_datum(mids[subject][metric], ts, value)

        self.num_collected += 1
        if self.num_collected >= self.config["reporting_params"]:
            self.report()
            self.num_collected = 0

    def _insert_datum(self, mid, ts, val):
        item = dict({"ts": ts * 10e5,
                     "value":val})
        self.mid_to_data[mid].append(item)

    def report(self):
        '''
        Send all data collected so far, then clear stored data.
        '''
        post_data = []
        for mid, data in self.mid_to_data.iteritems():
            if len(data):
                post_data.append({"mid":mid, "data":data})
        self.ms.post_data(post_data)
        self._clear_data()

    def _post_measurement(self):
        probe_mod = blipp_import(self.config["probe_module"])
        if "EVENT_TYPES" in probe_mod.__dict__:
            eventTypes = probe_mod.EVENT_TYPES.values()
        else:
            try:
                eventTypes = self.config["eventTypes"].values()
            except KeyError:
                logger.warn("_post_measurement", msg="No eventTypes present")
                eventTypes = []

        measurement = {}
        measurement["service"] = self.config["serviceRef"]
        measurement["configuration"] = self.config
        measurement["eventTypes"] = eventTypes
        r = self.unis.post("/measurements", measurement)
        self.measurement = r["selfRef"]


    def _clear_data(self):
        for mid in self.mid_to_data:
            self.mid_to_data[mid]=[]
