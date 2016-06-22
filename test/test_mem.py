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
'''
Created on Dec 11, 2012

@author: jaffee
'''
import unittest2
import mock
from cStringIO import StringIO
import consts
import blipp.mem

class MemProbeTests(unittest2.TestCase):
    def setUp(self):
        self.probe = blipp.mem.Probe()
        self.proc = mock.Mock()
        self.proc.open.return_value = StringIO(consts.meminfo)
        self.probe._proc = self.proc

    def test_get_data(self):
        self.proc.exists.return_value = StringIO(consts.user_beancounters)
        expected = {"ps:tools:blipp:linux:memory:utilization:free": 525460,
                    "ps:tools:blipp:linux:memory:utilization:kernel": 60474,
                    "ps:tools:blipp:linux:memory:utilization:used": 4693144}
        actual = self.probe.get_data()
        self.assertEqual(actual, expected)

    def test_get_data2(self):
        self.proc.exists.return_value = False
        expected = {"ps:tools:blipp:linux:memory:utilization:free": 525460,
                    "ps:tools:blipp:linux:memory:utilization:used": 7602504,
                    "ps:tools:blipp:linux:memory:utilization:buffer": 358700,
                    "ps:tools:blipp:linux:memory:utilization:cache": 4390548,
                    "ps:tools:blipp:linux:memory:utilization:kernel": 401292}

        actual = self.probe.get_data()
        self.assertEqual(actual, expected)

