import blipp.utils as utils
import unittest2

class UtilsTests(unittest2.TestCase):
    def setUp(self):
        self.ET1 = {
            'user':"ps:tools:blipp:linux:cpu:utilization:user",
            'system':"ps:tools:blipp:linux:cpu:utilization:system",
            'nice':"ps:tools:blipp:linux:cpu:utilization:nice"}
        self.ET2 = {
            "packets_in":"ps:tools:blipp:linux:network:ip:utilization:packets:in",
            "packets_out":"ps:tools:blipp:linux:network:ip:utilization:packets:out",
            "bytes_in":"ps:tools:blipp:linux:network:utilization:bytes:in"}
        pass

    def test_full_event_types(self):
        data = {'user': 4, 'system': 5, 'nice': 6}
        res = utils.full_event_types(data, self.ET1)
        desired = {"ps:tools:blipp:linux:cpu:utilization:user":4,
                   "ps:tools:blipp:linux:cpu:utilization:system":5,
                   "ps:tools:blipp:linux:cpu:utilization:nice": 6}
        self.assertEqual(res, desired)


    def test_full_event_types2(self):
        data = {
            "subject1":{"packets_in": 1,
                        "packets_out": 2,
                        "bytes_in": 3},
            "subject2":{"packets_in": 4,
                        "packets_out": 5,
                        "bytes_in": 6}}
        res = utils.full_event_types(data, self.ET2)
        desired = {
            "subject1":{"ps:tools:blipp:linux:network:ip:utilization:packets:in": 1,
                        "ps:tools:blipp:linux:network:ip:utilization:packets:out": 2,
                        "ps:tools:blipp:linux:network:utilization:bytes:in": 3},
            "subject2":{"ps:tools:blipp:linux:network:ip:utilization:packets:in": 4,
                        "ps:tools:blipp:linux:network:ip:utilization:packets:out": 5,
                        "ps:tools:blipp:linux:network:utilization:bytes:in": 6}}

        self.assertEqual(res, desired)

    def test_merge_dicts(self):
        d1 = {"a": {"b": 2, "c": 3},
              "x":1, "d":5, "e": {"f": {"g": {"a": 0, "h": "blarg"}}}}
        d2 = {"a": {"z":99},
              "d":12,
              "e": {
                "f": {
                    "g": {
                        "h": "glearb",
                        "i": "kwarb"}}}}
        merged = {"a": {"z":99, "b": 2, "c": 3},
                  "d": 12,
                  "x": 1,
                  "e": {
                "f": {
                    "g": {
                        "a": 0,
                        "h": "glearb",
                        "i": "kwarb"}}}}
        utils.merge_dicts(d1, d2)
        self.assertEqual(d1, merged)

    def test_delete_nones(self):
        d = {"a": 1, "b": None, "c": {"a": 1, "b": None, "d": {"a": None}}}
        utils.delete_nones(d)
        res = {"a": 1, "c": {"a": 1, "d": {}}}
        self.assertEqual(d, res)

if __name__ == '__main__':
    unittest2.main()
