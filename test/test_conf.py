import unittest2

from blipp.conf import IncompleteConfigError, ServiceConfigure


class ServiceConfigureTests(unittest2.TestCase):
    def setUp(self):
        print "ServiceConfigureTests setup"
        self.sconf = ServiceConfigure(file_loc="/usr/local/conf.conf",
                                      unis_url="http://example.com")

    def test__init__(self):
        print "ServiceConfigureTests init"
        self.assertRaises(IncompleteConfigError, ServiceConfigure,
                          service_name="blipp",
                          node_id="deadbeef7e57n0de",
                          service_id="deadbeef7e575e12v1ce")

    def test_refresh_config(self):
        pass


if __name__ == '__main__':
    unittest2.main()

