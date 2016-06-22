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
import settings
from periscope_client import PeriscopeClient

logger = settings.get_logger('ms_client')

class MSInstance:
    def __init__(self, service_entry, measurement):
        self.service_entry = service_entry
        self.sconfig = service_entry["properties"]["configurations"]
        self.mconfig = measurement["configuration"]
        self.ms_url=self.mconfig.get("ms_url", None)
        self.pc = PeriscopeClient(self.service_entry, self.ms_url)
        self.mids = set()

    def _def_headers(self, ctype):
        def_headers={'content-type':
                          'application/perfsonar+json profile=' + settings.SCHEMAS[ctype],
                          'accept':"*/*"}
        return def_headers

    def post_events(self, mid, size, ttl):
        data = dict({"metadata_URL": self.sconfig['unis_url'] + "/metadata/" + mid,
                     "collection_size": size,
                     "ttl": ttl
                     })
        headers = self._def_headers("datum")
        return self.pc.do_req('post', '/events', data, headers)

    def post_data(self, data):
        if not self.ms_url:
            return None
        mids = [ x["mid"] for x in data ]
        self._check_mids(mids)
        headers = self._def_headers("data")
        return self.pc.do_req('post', '/data', data, headers)

    def _check_mids(self, mids):
        coll_size = self.mconfig["collection_size"]
        coll_ttl = self.mconfig["collection_ttl"]
        for mid in mids:
            if mid not in self.mids:
                if not self.pc.get("/events?mids=" + str(mid)):
                    if self.post_events(mid, coll_size, coll_ttl):
                        self.mids.add(mid)
                else:
                    self.mids.add(mid)
