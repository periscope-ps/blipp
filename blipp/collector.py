from ms_client import MSInstance
from unis_client import UNISInstance
import settings
logger = settings.get_logger('collector')


class Collector:
    """Collects reported measurements and aggregates them for
    sending to MS at appropriate intervals.

    Also does a bunch of other stuff which should probably be handled by separate classes.
    Creates all the metadata objects, and the measurement object in UNIS for all data inserted.
    Depends directly on the MS and UNIS... output could be far more modular.
    """

    def __init__(self, service, measurement):
        self.config = measurement["configuration"]
        self.service = service
        self.measurement = measurement
        self.collections_created = False
        self.ms = MSInstance(service, measurement)
        self.mids = {} # {subject1: {metric1:mid, metric2:mid}, subj2: {...}}
        # {mid: [{"ts": ts, "value": val}, {"ts": ts, "value": val}]}
        self.mid_to_data = {}
        self.unis = UNISInstance(service)
        self.num_collected = 0

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
                if metric not in self.measurement["eventTypes"]:
                    self._add_et(metric)
                if not metric in mids.get(subject, {}):
                    r = self.unis.find_or_create_metadata(subject,
                                                          metric,
                                                          self.measurement)
                    mids.setdefault(subject, {})[metric] = r["id"]
                    self.mid_to_data[r["id"]] = []
                self._insert_datum(mids[subject][metric], ts, value)

        self.num_collected += 1
        if self.num_collected >= self.config["reporting_params"]:
            ret = self.report()
            if ret:
                self.num_collected = 0

    def _insert_datum(self, mid, ts, val):
        item = dict({"ts": ts * 10e5,
                     "value":val})
        self.mid_to_data[mid].append(item)

    def _add_et(self, metric):
        self.measurement["eventTypes"].append(metric)
        r = self.unis.put("/measurements/" +
                          self.measurement["id"],
                          data=self.measurement)
        if r:
            self.measurement = r

    def report(self):
        '''
        Send all data collected so far, then clear stored data.
        '''
        post_data = []
        for mid, data in self.mid_to_data.iteritems():
            if len(data):
                post_data.append({"mid":mid, "data":data})
        ret = self.ms.post_data(post_data)
        if not ret:
            return None
        self._clear_data()
        return post_data

    def _clear_data(self):
        for mid in self.mid_to_data:
            self.mid_to_data[mid]=[]
