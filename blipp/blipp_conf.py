# =============================================================================
#  periscope-ps (blipp)
#
#  Copyright (c) 2013-2016, Trustees of Indiana University,
#  All rights reserved.
#
#  This software may be modified and distributed under the terms of the BSD
#  license.  See the COPYING file for details.
#
#  This software was created at the Indiana University Center for Research in
#  Extreme Scale Technologies (CREST).
# =============================================================================
from .conf import ServiceConfigure
from .utils import blipp_import
from . import settings
from .validation import validate_add_defaults
from unis.models import Measurement

# should be blipp_conf, but netlogger doesn't like that for some reason
logger = settings.get_logger('confblipp')

class BlippConfigure(ServiceConfigure):
    def __init__(self, initial_config={}, node_id=None,
        pre_existing_measurements="ignore", urn=None):
        if "name" not in initial_config:
            initial_config['name']="blipp"
        self.pem = pre_existing_measurements
        self.probe_defaults = None
        self.measurements = []
        super(BlippConfigure, self).__init__(initial_config, node_id, urn)

    def initialize(self):
        def _get_eventTypes(p):
            mod = blipp_import(p['probe_module'])
            try:
                return list(mod.EVENT_TYPES)
            except AttributeError:
                logger.warn("Probe module has no EVENT_TYPES")
            try:
                return list(p['eventTypes'])
            except KeyError:
                logger.warn("Probe configuration missing eventTypes field")
            return []

        super(BlippConfigure, self).initialize()
        meas = set()
        remote = list(self.unis.measurements.where({'service': self.service}))
        for n,m in self.config['properties']['configurations']['probes'].items():
            p = {**self.config['properties']['configurations']['probe_defaults'], **m, **{'name': n}}
            m = self.unis.measurements.first_where(lambda x: x.service == self.service.selfRef and x.configuration.name == p['name']) or \
                self.unis.insert(Measurement(), commit=True)
            m.service = self.service.selfRef
            m.configuration = p
            m.eventTypes = _get_eventTypes(p)
            if getattr(m, 'scheduled_times', True) is None:
                del m.getObject().__dict__['scheduled_times']
            meas.add(m)

        if self.pem == "use":
            [meas.add(m) for m in remote]

        self.measurements = list(meas)
        self.unis.flush()

    def refresh(self):
        interval = super(BlippConfigure, self).refresh()
        [m.touch() for m in self.measurements]
        self.unis.flush()
        return interval

    def get_measurements(self):
        '''
        Return all measurements which are configured for this blipp
        instance. Possibly excluding those which where initially
        present when blipp started.
        '''
        return [m for m in self.measurements if getattr(m.configuration, "status", "OFF").upper() == "ON"]
