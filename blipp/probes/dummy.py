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
import time
from blipp.probes import abc


EVENT_TYPES={
    "dummy":"ps:testing:dummy"
}

class Probe(abc.Probe):
    """
    Dummy probe that just sleeps and returns 1
    """
    def get_data(self):
        time.sleep(getattr(getattr(self.config, "schedule_params", {}), "duration", 0))
        return {EVENT_TYPES["dummy"]: 1}
