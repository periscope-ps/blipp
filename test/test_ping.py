import unittest2
import mock
import re
from blipp.ping import Probe,NonMatchingOutputError,UnknownUnitsError,PingError

class PingProbeTests(unittest2.TestCase):
    def setUp(self):
        self.ping_probe = Probe({})

    def test_extract_data(self):
        output = '''PING google.com (74.125.225.8) 56(84) bytes of data.
64 bytes from ord08s05-in-f8.1e100.net (74.125.225.8): icmp_req=1 ttl=54 time=23.1 ms

--- google.com ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 23.141/23.141/23.141/0.000 ms'''
        data_dict = self.ping_probe._extract_data(output)
        self.assertEqual(data_dict['ttl'], '54')
        self.assertEqual(data_dict['rtt'], '23.1')

    def test_extract_data2(self):
        output = '''alksjdflkjsalkdjf'''

        self.assertRaises(NonMatchingOutputError,
                          self.ping_probe._extract_data, output)

    def test_extract_data3(self):
        output = '''64 bytes from ord08s05-in-f8.1e100.net (74.125.225.8): icmp_req=1 ttl=54 time=23.1 s'''
        self.assertRaises(UnknownUnitsError, self.ping_probe._extract_data, output)

    def test_get_data(self):
        subproc = mock.Mock()
        get_subproc = mock.Mock()
        get_subproc.return_value = subproc
        subproc.communicate.return_value = ('',
                                            'ping: unknown host ' + self.ping_probe.address)

        self.ping_probe._get_subprocess = get_subproc
        self.assertRaises(PingError, self.ping_probe.get_data)
