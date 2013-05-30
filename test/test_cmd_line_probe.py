import unittest2
from blipp import cmd_line_probe
import shlex


class CmdLineProbeTests(unittest2.TestCase):

    def test_init(self):
        # basically tests _substitute_command
        config = {
            '$schema': 'http://unis.incntre.iu.edu/schema/blippmeasurements/20130429/ping#',
            'address': 'iu.edu',
            'command': 'ping -c 1 $-W $-s $-t $-p $-M $-Q $address',
            'eventTypes': {'rtt': 'ps:tools:blipp:linux:net:ping:rtt',
                           'ttl': 'ps:tools:blipp:linux:net:ping:ttl'},
            '-M': 'dont',
            '-s': 56,
            '-p': '00',
            '-t': 60,
            'probe_module': 'cmd_line_probe',
            'name': "my_test_ping_probe",
            'regex': 'ttl=(?P<ttl>\\d+).*time=(?P<rtt>\\d+\\.\\d+) ',
            '-W': 2,
            '-Q': '0'}
        cmd_probe = cmd_line_probe.Probe(config)
        expected = shlex.split("ping -c 1 -W 2 -s 56 -t 60 -p 00 -M dont -Q 0 iu.edu")
        self.assertEqual(cmd_probe.command, expected)
