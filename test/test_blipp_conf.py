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
import unittest2
from blipp.blipp_conf import BlippConfigure
import consts
from copy import deepcopy


class BlippConfigureTests(unittest2.TestCase):
    def setUp(self):
        self.sconf = BlippConfigure(initial_config={"properties":
                                                    {"configurations":
                                                     {"unis_url": "http://example.com"}}})
        self.sconf.config = deepcopy(consts.SAMPLE_CONFIG)

    def test_expand_probe_config(self):
        probe_list = self.sconf.expand_probe_config()

        ping1 = consts.PING_1
        ping2 = consts.PING_2
        self.assertTrue(ping1 in probe_list)
        self.assertTrue(ping2 in probe_list)
        self.assertTrue(len(probe_list)==4)

        probe_list2 = self.sconf.expand_probe_config()
        self.assertEqual(probe_list, probe_list2)

    def test_expand_probe_config_with_schema(self):
        self.sconf.config["properties"]["configurations"]["probes"]["pingschema"] = {
            "$schema": "file://ping-schema.json",
            "address": "iu.edu"
        }
        pingschema = consts.PING_SCHEMA
        probe_list = self.sconf.expand_probe_config()
        self.assertTrue(pingschema in probe_list)

    def test_strip_probes(self):
        sampleconf = deepcopy(consts.SAMPLE_CONFIG)
        probes = BlippConfigure._strip_probes(sampleconf)
        self.assertEqual(sampleconf, consts.SAMPLE_STRIPPED)
        self.assertEqual(probes, consts.STRIPPED_PROBES)

if __name__ == '__main__':
    unittest2.main()
