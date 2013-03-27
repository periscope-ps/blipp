from ms_client import MSInstance
from unis_client import UNISInstance
import settings
logger = settings.get_logger('collector')


class Collector:
    """Collects reported measurements and aggregates them for
    sending to MS at appropriate intervals.
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

    def insert(self, data, ts):
        mids = self.mids
        for subject, met_val in data.iteritems():
            for metric, value in met_val.iteritems():
                if not metric in mids.get(subject, {}):
                    r = self.unis.post_metadata(subject, metric, self.config)
                    mids.setdefault(subject, {})[metric] = r["id"]
                    self.mid_to_data[r["id"]] = []
                self._insert_datum(mids[subject][metric], ts, value)

        self.num_collected += 1
        if self.num_collected >= self.config["reporting_params"]:
            self.report()
            self.num_collected = 0

    def _insert_datum(self, mid, ts, val):
        item = dict({"ts": ts * 1000000,
                     "value":val})
        self.mid_to_data[mid].append(item)

    def report(self):
        data = [ dict({"mid":mid, "data":data})
                 for mid, data in self.mid_to_data.iteritems() ]
        self.ms.post_data(data)
        self._clear_data()

    def _clear_data(self):
        for mid in self.mid_to_data:
            self.mid_to_data[mid]=[]
