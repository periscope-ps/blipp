from conf import ServiceConfigure
from utils import merge_into, blipp_import, get_most_recent
from schema_cache import SchemaCache
import settings
from validation import validate_add_defaults

import pprint

# should be blipp_conf, but netlogger doesn't like that for some reason
logger = settings.get_logger('confblipp')

class BlippConfigure(ServiceConfigure):
    def __init__(self, initial_config={}, node_id=None,
        pre_existing_measurements="ignore", urn=None):
        if "name" not in initial_config:
            initial_config['name']="blipp"
        self.pem = pre_existing_measurements
        self.schema_cache = SchemaCache()
        self.probe_defaults = None
        self.measurements = []
        super(BlippConfigure, self).__init__(initial_config, node_id, urn)

    def initialize(self):
        super(BlippConfigure, self).initialize()
        if not self.service_setup:
            logger.error("initialize", msg="Could not reach UNIS to initialize service")
            exit(-1)
        self.initial_measurements = self.unis.get("/measurements?service=" +
                                                  self.config["selfRef"])
        self.initial_measurements = get_most_recent(self.initial_measurements)
        # use any pre-existing measurements found in UNIS right away
        if self.pem=="use":
            for m in self.initial_measurements:
                self.measurements.append(m)
        # now strip and add to measurements any probes found in the merged initial config
        self.initial_probes = self._strip_probes(self.config)
        if self.initial_probes:
            self._post_probes()
            self.unis.put("/services/" + self.config["id"], data=self.config)

    def _post_probes(self):
        failed_probes = {}
        for name,probe in self.initial_probes.items():
            probe.update({"name": name})
            try:
                probe = self._validate_schema_probe(probe)
            except Exception as e:
                logger.exc('_post_probes', e)
                continue # skip this probe
            r = self._post_measurement(probe)
            if not r:
                failed_probes[name] = probe
            else:
                # add the measurement to our internal list right away
                self.measurements.append(r)
        self.initial_probes = failed_probes
        if failed_probes:
            logger.warn('_post_probes', failed_probes=pprint.pformat(failed_probes))

    def _validate_schema_probe(self, probe):
        if "$schema" in probe:
            schema = self.schema_cache.get(probe["$schema"])
            validate_add_defaults(probe, schema)
        return probe

    def refresh(self):
        interval = super(BlippConfigure, self).refresh()
        if interval != 0:
            return interval
        
        # unis.get returns a list of config
        if isinstance(self.config, list):
            self.config = self.config[0]
        
        self.initial_probes = self._strip_probes(self.config)
        if self.initial_probes:
            self._post_probes()
            self.unis.put("/services/" + self.config["id"], data=self.config)
        qmeas = self.unis.get("/measurements?service=" +
                              self.config["selfRef"])
        if qmeas:
            self.measurements = qmeas
            self.measurements = get_most_recent(self.measurements)
            for m in self.measurements:
                size_orig = len(m["configuration"])
                merge_into(m["configuration"], self.probe_defaults)
                if size_orig < len(m["configuration"]):
                    self.unis.put("/measurements/"+m["id"], m)
        else:
            ''' If measurements don't exist then create them again - i.e register them again '''
            self.measurements = get_most_recent(self.measurements)
            for m in self.measurements:
                self.unis.post("/measurements/", m)
        
        return interval

    def _post_measurement(self, probe):
        probe_mod = blipp_import(probe["probe_module"])
        if "EVENT_TYPES" in probe_mod.__dict__:
            eventTypes = probe_mod.EVENT_TYPES.values()
        else:
            try:
                eventTypes = probe["eventTypes"].values()
            except KeyError:
                logger.warn("_post_measurement", msg="No eventTypes present")
                eventTypes = []

        measurement = {}
        measurement["service"] = self.config["selfRef"]

        measurement["configuration"] = probe
        measurement["eventTypes"] = eventTypes
        r = self.unis.post("/measurements", measurement)
        return r

    def get_measurements(self):
        '''
        Return all measurements which are configured for this blipp
        instance. Possibly excluding those which where initially
        present when blipp started.
        '''
        measurements = []
        for m in self.measurements:
            if self.pem=="use":
                measurements.append(m)
            elif m not in self.initial_measurements:
                measurements.append(m)
        
        return filter(lambda m: m["configuration"].get("status", "ON").upper()=="ON", measurements)

    def _strip_probes(self, initial_config):
        probes = {}
        try:
            probes = initial_config["properties"]["configurations"]["probes"]
            del initial_config["properties"]["configurations"]["probes"]
        except Exception:
            pass
        try:    
            probe_defaults = initial_config["properties"]["configurations"]["probe_defaults"]
            self.probe_defaults = probe_defaults
        except Exception:
            pass
        
        if probes:
            for probe in probes.values():
                merge_into(probe, self.probe_defaults)

        return probes
