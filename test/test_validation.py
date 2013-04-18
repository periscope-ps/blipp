from blipp import validation
import json
import unittest2

class ValidationTests(unittest2.TestCase):

    def test_add_defaults(self):
        schema = json.loads(open("ping-schema.json").read())
        conf = {"address": "example.com",
                "ttl": 48
            }
        validation.validate_add_defaults(conf, schema)
        expected = {
            u'$schema': u'http://unis.incntre.iu.edu/schema/blippmeasurements/20130416/ping#',
            u'probe_module': u'cmd_line_probe',
            u'command': u'ping -W $TIMEOUT -s $PACKET_SIZE -t $TTL -p $PATTERN -M $HINT -Q $TOS $EXTRAARGS $ADDRESS',
            u'regex': u'ttl=(?P<ttl>\\d+).*time=(?P<rtt>\\d+\\.\\d+) ',
            u'eventTypes': {
		u'ttl': u'ps:tools:blipp:linux:net:ping:ttl',
		u'rtt': u'ps:tools:blipp:linux:net:ping:rtt'
	    },
            u'timeout': 2,
            u'packet_size': 56,
            'ttl': 48,
            u'pattern': u'00',
            u'hint': u'dont',
            u'tos': u'0',
            u'extraargs': u'',
            'address': 'example.com'
        }
        self.assertEqual(conf, expected)
