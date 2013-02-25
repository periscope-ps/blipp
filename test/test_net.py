import unittest2
import mock
from blipp.net import Probe

class NetProbeTests(unittest2.TestCase):
    def setUp(self):
        Probe.get_interface_subjects=mock.Mock()
        Probe.get_interface_subjects.return_value = {"lo": "unisurlforlo",
                                                     "pan0": "unisurlforpan0",
                                                     "wlan0": "unisurlforwlan0",
                                                     "eth0": "unisurlforeth0"}
        self.net_probe = Probe()
        self.dev_string = ''' face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    lo:16437577  120248    0    0    0     0          0         0 16437577  120248    0    0    0     0       0          0
  eth0:12267757  166430    0    0    0     0          0      2832 30458998  143263    0    0    0     0       0          0
 wlan0:5029574829 7333434    0    0    0     0          0         0 887097774 4036590    0    0    0     0       0          0
  pan0:       0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
'''

    def test_get_dev_data(self):
        data = self.net_probe._get_dev_data(self.dev_string)
        ddata = {'unisurlforeth0': {'bytes_in': 12267757,
          'bytes_out': 30458998,
          'errors': 0,
          'drops': 0,
          'packets_in': 166430,
          'packets_out': 143263},
 'unisurlforlo': {'bytes_in': 16437577,
        'bytes_out': 16437577,
        'errors': 0,
        'drops': 0,
        'packets_in': 120248,
        'packets_out': 120248},
 'unisurlforpan0': {'bytes_in': 0,
          'bytes_out': 0,
          'errors': 0,
          'drops': 0,
          'packets_in': 0,
          'packets_out': 0},
 'unisurlforwlan0': {'bytes_in': 5029574829,
           'bytes_out': 887097774,
           'errors': 0,
           'drops': 0,
           'packets_in': 7333434,
           'packets_out': 4036590}}
        self.assertEqual(ddata, data)

    def test_get_snmp_data(self):
        netsnmp = '''Ip: Forwarding DefaultTTL InReceives InHdrErrors InAddrErrors ForwDatagrams InUnknownProtos InDiscards InDelivers OutRequests OutDiscards OutNoRoutes ReasmTimeout ReasmReqds ReasmOKs ReasmFails FragOKs FragFails FragCreates
Ip: 2 64 5449663 1723 786 0 0 0 5279316 4258836 4 16375 0 0 0 0 0 0 0
Icmp: InMsgs InErrors InDestUnreachs InTimeExcds InParmProbs InSrcQuenchs InRedirects InEchos InEchoReps InTimestamps InTimestampReps InAddrMasks InAddrMaskReps OutMsgs OutErrors OutDestUnreachs OutTimeExcds OutParmProbs OutSrcQuenchs OutRedirects OutEchos OutEchoReps OutTimestamps OutTimestampReps OutAddrMasks OutAddrMaskReps
Icmp: 32861 1658 32663 24 0 0 0 39 135 0 0 0 0 17212 0 17033 0 0 0 0 140 39 0 0 0 0
IcmpMsg: InType0 InType3 InType8 InType11 OutType0 OutType3 OutType8
IcmpMsg: 135 32663 39 24 39 17033 140
Tcp: RtoAlgorithm RtoMin RtoMax MaxConn ActiveOpens PassiveOpens AttemptFails EstabResets CurrEstab InSegs OutSegs RetransSegs InErrs OutRsts
Tcp: 1 200 120000 -1 157584 174 17508 10834 7 4660605 3841483 20035 1 20939
Udp: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors SndbufErrors
Udp: 509585 1264 0 374940 0 0
UdpLite: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors SndbufErrors
UdpLite: 0 0 0 0 0 0
'''
        data = self.net_probe._get_snmp_data(netsnmp)
        ddata = {'datagrams_in': 509585,
                 'datagrams_out': 374940,
                 'tcp_retrans': 20035,
                 'tcp_segments_in': 4660605,
                 'tcp_segments_out': 3841483}
        self.assertEqual(data, ddata)
