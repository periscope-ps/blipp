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
from blipp.probe_runner import ProbeRunner
import consts
import mock

class ProbeRunnerTests(unittest2.TestCase):
    def setUp(self):
        psetup = ProbeRunner.setup
        ProbeRunner.setup = mock.Mock()
        self.prunner = ProbeRunner(consts.PING_1)
        ProbeRunner.setup = psetup
        self.prunner.setup = psetup

    def test_setup(self):
        prunner = self.prunner
        prunner.setup(prunner)
        self.assertEqual(str(prunner.probe.__class__)[-10:], 'ping.Probe')
        self.assertEqual(str(prunner.scheduler.__class__), "<type 'generator'>")
        num1 = prunner.scheduler.next()
        num2 = prunner.scheduler.next()
        self.assertEqual(num1+5, num2)

    def test_normalize(self):
        prunner = self.prunner
        data1 = {'metric1':5, 'metric2':10, 'metric3':8}
        data1_norm = {"http://dev.incntre.iu.edu/nodes/anode": {'metric1':5, 'metric2':10, 'metric3':8}}
        data2 = {'subject1':{'metric1':5}, 'subject2':{'metric2':10, 'metric3':8}}
        self.assertEqual(prunner._normalize(data1), data1_norm)
        self.assertEqual(prunner._normalize(data2), data2)
