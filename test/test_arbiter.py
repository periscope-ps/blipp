import unittest2
import mock
from blipp.blipp_conf import BlippConfigure
from blipp import arbiter
import consts
import time


class ArbiterTests(unittest2.TestCase):
    def setUp(self):
        self.bconf = BlippConfigure(initial_config={"properties":
                                                    {"configurations":
                                                     {"unis_url": "http://example.com"}}})
        self.bconf.config = consts.SAMPLE_CONFIG
        self.bconf.refresh_config = mock.Mock()
        self.probe_runner = mock.Mock()
        arbiter.ProbeRunner = self.probe_runner
        self.pr = mock.Mock()
        self.probe_runner.return_value = self.pr
        self.pr.run = loop
        self.arb = arbiter.Arbiter(self.bconf)

    def test_reload_all(self):
        self.arb.reload_all()
        self.assertTrue(len(self.arb.proc_to_config)==4)
        proc2config1 = str(self.arb.proc_to_config)
        self.arb.reload_all()
        proc2config2 = str(self.arb.proc_to_config)
        self.assertTrue(proc2config2 == proc2config1)

    def test_reload_all2(self):
        self.arb.reload_all()
        self.arb._start_new_probe = mock.Mock()
        self.arb._stop_probe = mock.Mock()
        self.arb.reload_all()
        self.assertTrue(not self.arb._start_new_probe.called)
        self.assertTrue(not self.arb._stop_probe.called)

    def test_reload_all3(self):
        self.arb.reload_all()
        for proc, conn in self.arb.proc_to_config.keys():
            proc.terminate()
            while proc.is_alive(): pass
            break

        self.arb._check_procs()
        self.assertTrue(len(self.arb.proc_to_config)==3)
        self.arb.reload_all()
        self.assertTrue(len(self.arb.proc_to_config)==4)

    def test_reload_all4(self):
        self.arb.reload_all()
        self.bconf.config["properties"]["configurations"]["probes"]["ping1"]["schedule_params"] = {"every":9}
        self.arb._start_new_probe = mock.Mock()
        self.arb._stop_probe = mock.Mock()
        self.arb.reload_all()
        self.assertEqual(self.arb._start_new_probe.call_count, 1)
        self.assertEqual(self.arb._stop_probe.call_count, 1)

    def test_reload_all5(self):
        # test status off functionality
        self.arb.config = mock.Mock()
        self.arb.config.get.return_value = "OFF"
        self.arb._stop_all = mock.Mock()
        self.arb.reload_all()
        self.assertEqual(self.arb.proc_to_config, {})
        self.assertEqual(self.arb.stopped_procs, {})
        self.assertTrue(self.arb._stop_all.called)

    def test_cleanup_stopped_probes(self):
        '''regression test - make sure cleanup stopped probes doesn't
        try to delete from the dict it's iterating over'''
        key1 = mock.Mock()
        key1.is_alive.return_value = False
        key2 = mock.Mock()
        self.arb.stopped_procs = {(key1, "conn1"): 333000222, (key1, "conn2"): 333111222, (key2, "conn3"): 333222222}
        self.arb._cleanup_stopped_probes()

    def tearDown(self):
        for proc, conn in self.arb.proc_to_config.keys():
            proc.terminate()


def loop(anarg):
    while True:
        if anarg.poll():
            if anarg.recv()=="stop":
                break
        time.sleep(.1)


if __name__ == '__main__':
    unittest2.main()
