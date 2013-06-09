import unittest2
import mock
from blipp.conf import ServiceConfigure


class ServiceConfigureTests(unittest2.TestCase):
    def setUp(self):
        print "ServiceConfigureTests setup"
        ServiceConfigure._get_file_config = mock.Mock()
        ServiceConfigure._get_file_config.return_value = {}

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
