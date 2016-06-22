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
from blipp.unis_client import UNISInstance

unis = UNISInstance({"unis_url":"http://dev.incntre.iu.edu"})
s = unis.get("/services?name=blipp&properties.configurations.hostname=hikerbear")
s = s if s else []
s2 = unis.get("/services?name=blipp&runningOn.href=http://dev.incntre.iu.edu/nodes/510b3492e77989124500008f")
s2 = s2 if s2 else []

s.extend(s2)

for serv in s:
    unis.delete("/services/" + serv["id"])



