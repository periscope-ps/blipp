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
from .utils import clean_mac

def mac_match(geni_port, local_port):
    try:
        geni_mac = clean_mac(geni_port.properties.geni.mac_address)
    except AttributeError:
        try:
            geni_mac = clean_mac(geni_port.properties.mac.address)
        except KeyError:
            return False
    try:
        local_mac = clean_mac(local_port['properties']['mac']['address'])
    except KeyError:
        return False
    return local_mac == geni_mac
