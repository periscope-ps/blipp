# =============================================================================
#  periscope-ps (blipp)
#
#  Copyright (c) 2013-2016, Trustees of Indiana University,
#  All rights reserved.
#
#  This software may be modified and distributed under the terms of the BSD
#  license.  See the COPYING file for details.
#
#  This software was created at the Indiana University Center for Research in
#  Extreme Scale Technologies (CREST).
# =============================================================================
import unittest2
import mock
import blipp.ms_client as msc


class MSInstanceTests(unittest2.TestCase):
    def setUp(self):
        config = {"ms_url": "fakeurl",
                  "collection_size": 100,
                  "collection_ttl": 200}
        self.ms = msc.MSInstance(config)

    def test_post_data(self):
        data = [
            {"mid": "testmid1",
             "data": [{"ts": 12345, "value": 112345},
                      {"ts": 23456, "value": 123456}]},
            {"mid": "testmid2",
             "data": [{"ts": 54321, "value": 254321},
                      {"ts": 65432, "value": 265432}]}
            ]
        self.ms.gc = mock.Mock()
        self.ms._check_mids = mock.Mock()

        self.ms.post_data(data)
        self.ms._check_mids.assert_called_with(["testmid1", "testmid2"])
        self.ms.gc.do_req.assert_called_with('post', '/data', data, {'content-type':
                          'application/perfsonar+json profile=http://unis.incntre.iu.edu/schema/20140214/data#',
                          'accept':"*/*"})

    def test_check_mids(self):
        self.ms.mids.add('testmid3')
        self.ms.post_events=mock.Mock()

        self.ms.post_events.side_effect =\
            lambda *x: {('testmid1', 100, 200): None, ('testmid2', 100, 200): True}[x]

        self.ms.gc.get = mock.Mock()
        self.ms.gc.get.return_value = None



        self.ms._check_mids(["testmid1", "testmid2"])

        self.assertEqual(self.ms.gc.get.call_count, 2)
        self.ms.gc.get.assert_any_call("/events?mids=testmid1")
        self.ms.gc.get.assert_any_call("/events?mids=testmid2")

        self.assertEqual(self.ms.post_events.call_count, 2)
        self.ms.post_events.assert_any_call('testmid1', 100, 200)
        self.ms.post_events.assert_any_call('testmid2', 100, 200)

        self.assertTrue('testmid2' in self.ms.mids)
        self.assertFalse('testmid1' in self.ms.mids)
