from conf import ServiceConfigure
from copy import deepcopy
from utils import merge_into
from schema_cache import SchemaCache
from validation import validate_add_defaults
import settings

logger = settings.get_logger('blipp_conf')

class BlippConfigure(ServiceConfigure):
    def __init__(self, file_loc=None, unis_url=None, service_id=None,
                 node_id=None, service_name=None, query_service=True):
        if service_name==None:
            service_name="blipp"
        self.schema_cache = SchemaCache()
        super(BlippConfigure, self).__init__(file_loc, unis_url, service_id,
                                             node_id, service_name, query_service)

    def expand_probe_config(self):
        probes = self.config["properties"]["configurations"]["probes"]
        expanded_probes = []
        defaults = self.make_defaults()
        for name, pconf in probes.items():
            probe = {}
            probe["name"] = name
            probe.update(pconf)
            merge_into(probe, defaults)
            if probe.has_key("$schema"):
                try:
                    schema = self.schema_cache.get(probe["$schema"])
                    validate_add_defaults(probe, schema)
                except Exception as e:
                    logger.exc('expand_probe_config', e)
                    continue
            expanded_probes.append(probe)

        return expanded_probes

    def make_defaults(self):
        defaults = {}
        defaults["runningOn"] = self.config["runningOn"]
        props = deepcopy(self.config["properties"])
        del props["configurations"]
        defaults["properties"] = props
        for k,v in self.config["properties"]["configurations"].items():
            if k is not "probe_defaults" and k is not "probes":
                defaults[k] = v
        for k,v in self.config["properties"]["configurations"]["probe_defaults"].items():
            defaults[k] = v
        return defaults
