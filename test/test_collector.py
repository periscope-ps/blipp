import unittest2
from mock import Mock
from blipp.collector import Collector


class CollectorTests(unittest2.TestCase):
    def setUp(self):
        self.collector = Collector({"unis_url": "NONE"})

    def test_insert(self):
        c = self.collector
        class post_metadata():
            def __init__(self):
                self.vals = [1234, 2234, 3234, 4234]
                self.i = -1
            def next(self, *args):
                self.i += 1
                return {"id":self.vals[self.i]}

        c.unis = Mock()
        c.unis.post_metadata = post_metadata().next
        data = {"subj1":{"metric1":"valsubj1met1", "metric2":"valsubj1met2"},
                "subj2":{"metric3":"valsubj2met3", "metric4":"valsubj2met4"}}
        ts = 1092837465
        c.insert(data, ts)
        for mid in c.mid_to_data.keys():
            self.assertTrue(mid in [1234, 2234, 3234, 4234])
        self.assertEqual(c.mid_to_data[3234][0]["value"], "valsubj2met3")



