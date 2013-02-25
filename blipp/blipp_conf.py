from conf import ServiceConfigure
from copy import deepcopy
from utils import merge_dicts


class BlippConfigure(ServiceConfigure):
    def __init__(self, file_loc=None, unis_url=None, service_id=None,
                 node_id=None, service_name=None, query_service=True):
        if service_name==None:
            service_name="blipp"
        super(BlippConfigure, self).__init__(file_loc, unis_url, service_id,
                                             node_id, service_name, query_service)

    def expand_probe_config(self):
        '''Configuration for probes has 3 levels, there are the
           service level probe_defaults, the defaults for each probe
           under "probes", and then specific config under "targets"
           for each actual instance of that particular
           probe. "targets" may not exist in which case there is one
           instance of that probe type. Each probe instance's actual
           config is the top level default, overidden by anything in
           probe_defaults, which in turn is overridden by anything in
           "targets".  This method returns a list of the final probe
           instances and their configurations
        '''
        probes = self.config["properties"]["configurations"]["probes"]
        probe_defaults = self.config["properties"]["configurations"]["probe_defaults"]
        configurations = deepcopy(self.config["properties"]["configurations"])
        del configurations["probe_defaults"]
        del configurations["probes"]
        probelist = []
        for name,probe in probes.iteritems():
            if "targets" in probe:
                targets = probe["targets"]
                for target in targets:
                    pconf = deepcopy(configurations)
                    merge_dicts(pconf, probe_defaults)
                    merge_dicts(pconf, probe)
                    del pconf["targets"]
                    merge_dicts(pconf, target)
                    pconf["name"] = name
                    probelist.append(pconf)
            else:
                pconf = deepcopy(configurations)
                merge_dicts(pconf, probe_defaults)
                merge_dicts(pconf, probe)
                pconf["name"] = name
                probelist.append(pconf)

        self._add_extra_fields(probelist)
        return probelist

    def _add_extra_fields(self, probelist):
        other_props = deepcopy(self.config["properties"])
        del other_props["configurations"]
        for probe in probelist:
            probe["runningOn"] = self.config["runningOn"]

            probeprops = probe.setdefault("properties", {})
            probeprops.update(other_props)
            for prop,val in other_props.iteritems():
                probeprops[prop]=val






