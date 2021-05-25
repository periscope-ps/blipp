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
from blipp import settings
from blipp import utils

from collections import defaultdict
from unis.models import Metadata

import pprint

logger = settings.get_logger('collector')

class Collector:
    """Collects reported measurements and aggregates them for
    sending to MS at appropriate intervals.

    Also does a bunch of other stuff which should probably be handled by separate classes.
    Creates all the metadata objects, and the measurement object in UNIS for all data inserted.
    Depends directly on the MS and UNIS... output could be far more modular.
    """

    def __init__(self):
        self.unis = utils.get_unis()
        self.mds = {}
        self.cache = defaultdict(list)

    def insert(self, data, measurement, ts):
        '''
        Called (by arbiter) to insert new data into this collector object.
        '''
        for subject, met_val in data.items():
            if isinstance(subject, str):
                try: subject = self.unis.find(subject)[0]
                except IndexError:
                    logger.warn(f"Invalid subject reference - '{subject}'")
            ts = met_val.get('ts', ts)
            for ty, v in met_val.items():
                _match = lambda x: x.measurement == measurement and x.eventType == ty
                if ty == 'ts': continue
                m = self.mds.get((subject, ty), None)
                if not m:
                    if ty not in measurement.eventTypes:
                        measurement.eventTypes.append(ty)

                    m = self.unis.metadata.first_where(_match)
                    if m is None:
                        d = {
                            'eventType': ty,
                            'parameters': {
                                'datumSchema': settings.SCHEMAS["datum"],
                            }
                        }
                        m = self.unis.insert(Metadata(d), commit=True)
                        m.subject = subject
                        m.parameters.measurement = self.measurement
                        self.unis.flush()
                    m.data._batch = int(self.config.reporting_params)
                    self.mds[(subject, ty)] = m
                    
                m.data.append(v, ts=ts*10e5)
        self.unis.flush()
