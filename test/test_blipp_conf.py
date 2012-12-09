import unittest2
from blipp.blipp_conf import BlippConfigure
import consts


class BlippConfigureTests(unittest2.TestCase):
    def setUp(self):
        self.sconf = BlippConfigure(file_loc="/usr/local/conf.conf",
                                      unis_url="http://example.com")
        self.sconf.config = consts.SAMPLE_CONFIG

    def test_expand_probe_config(self):
        probe_list = self.sconf.expand_probe_config()

        ping1 = consts.PING_1
        ping2 = consts.PING_2

        self.assertTrue(ping1 in probe_list)
        self.assertTrue(ping2 in probe_list)
        self.assertTrue(len(probe_list)==4)

        probe_list2 = self.sconf.expand_probe_config()
        self.assertEqual(probe_list, probe_list2)


if __name__ == '__main__':
    unittest2.main()
