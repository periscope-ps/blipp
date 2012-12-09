'''
Created on Dec 9, 2012

@author: jaffee
'''
import unittest2
import mock
from blipp.cpu import Probe
from blipp.cpu import EVENT_TYPES as ET

class CpuProbeTests(unittest2.TestCase):
    def setUp(self):
        self.cpu_probe = Probe()
        proc = mock.Mock()
        mock_file = mock.Mock()
        mock_file.readline.return_value =  "cpu  3579530 297982 559622 300054967 35610 5109 20004 0 0"
        proc.open.return_value = mock_file
        self.cpu_probe._proc = proc

    def test_get_data(self):
        total = 0.0
        for key,value in self.cpu_probe.get_data().items():
            if key==ET["fivemin"] or key==ET["fifteenmin"] or key==ET["onemin"]:
                pass
            else:
                total+=value
        self.assertEqual(total, 1.0)

        for key,value in self.cpu_probe.get_data().items():
            if key==ET["fivemin"] or key==ET["fifteenmin"] or key==ET["onemin"]:
                pass
            else:
                self.assertEqual(value, 0.0)



if __name__ == '__main__':
   unittest2.main()
