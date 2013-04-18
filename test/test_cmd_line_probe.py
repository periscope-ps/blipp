import unittest2
from blipp import cmd_line_probe
import shlex


class CmdLineProbeTests(unittest2.TestCase):

    def test_init(self):
        # basically tests _substitute_command
        config = {
            '$schema': 'http://unis.incntre.iu.edu/schema/blippmeasurements/20130416/ping#',
            'address': 'iu.edu',
            'command': 'ping -W $TIMEOUT -s $PACKET_SIZE -t $TTL -p $PATTERN -M $HINT -Q $TOS $EXTRAARGS $ADDRESS',
            'eventTypes': {'rtt': 'ps:tools:blipp:linux:net:ping:rtt',
                           'ttl': 'ps:tools:blipp:linux:net:ping:ttl'},
            'extraargs': '',
            'hint': 'dont',
            'packet_size': 56,
            'pattern': '00',
            'ttl': 60,
            'probe_module': 'cmd_line_probe',
            'regex': 'ttl=(?P<ttl>\\d+).*time=(?P<rtt>\\d+\\.\\d+) ',
            'timeout': 2,
            'tos': '0'}
        cmd_probe = cmd_line_probe.Probe(config)
        expected = shlex.split("ping -W 2 -s 56 -t 60 -p 00 -M dont -Q 0 iu.edu")
        self.assertEqual(cmd_probe.command, expected)
