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

if __name__ == '__main__':
    unittest2.main()
