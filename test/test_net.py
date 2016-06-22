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
import blipp.net
import net_consts

class NetProbeTests(unittest2.TestCase):
    def setUp(self):
        mock_gu = mock.Mock()
        mock_unis = mock.Mock()
        gn = mock.Mock()
        pp = mock.Mock()
        mock_gu.return_value = mock_unis
        mock_unis.get_node.return_value = gn
        mock_unis.post_port = pp
        blipp.net.Probe._get_unis = mock_gu
        gn.get.return_value = []
        pp.return_value = None

        self.net_probe = blipp.net.Probe()
        self.net_probe.subjects = {"lo": "unisurlforlo",
                                                     "pan0": "unisurlforpan0",
                                                     "wlan0": "unisurlforwlan0",
                                                     "eth0": "unisurlforeth0"}
        self.net_probe._get_unis = mock.Mock()
        self.dev_string = net_consts.dev_string

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
        netsnmp = net_consts.netsnmp
        data = self.net_probe._get_snmp_data(netsnmp)
        ddata = {'datagrams_in': 509585,
                 'datagrams_out': 374940,
                 'tcp_retrans': 20035,
                 'tcp_segments_in': 4660605,
                 'tcp_segments_out': 3841483}
        self.assertEqual(data, ddata)

    def test_get_interfaces_in_unis(self):
        mock_unis = mock.Mock()
        self.net_probe._get_unis.return_value = mock_unis
        mock_unis.get_node.return_value = net_consts.node1
        mock_unis.get.return_value = net_consts.port1
        expected = [net_consts.port1, net_consts.port1, net_consts.port1]
        ret = self.net_probe.get_interfaces_in_unis()
        self.assertEqual(ret, expected)

    def test_find_or_post_port(self):
        mmethod = mock.Mock()
        ports = [net_consts.port1]
        local_port = net_consts.local_port
        mmethod.return_value = True
        ret = self.net_probe._find_or_post_port(ports, local_port, mmethod)
        expected = net_consts.port1["selfRef"]
        self.assertEqual(ret, expected)

    def test_find_or_post_port2(self):
        mmethod = mock.Mock()
        mock_unis = mock.Mock()
        self.net_probe._get_unis.return_value = mock_unis
        ports = [net_consts.port1]
        local_port = net_consts.local_port
        mmethod.return_value = False
        mock_unis.post_port.return_value = net_consts.local_port_resp

        ret = self.net_probe._find_or_post_port(ports, local_port, mmethod)

        expected = net_consts.local_port_resp["selfRef"]
        self.assertEqual(ret, expected)

    def test_find_or_post_port3(self):
        mmethod = mock.Mock()
        mock_unis = mock.Mock()
        self.net_probe._get_unis.return_value = mock_unis
        ports = [net_consts.port1]
        local_port = net_consts.local_port
        mmethod.return_value = False
        mock_unis.post_port.return_value = None

        ret = self.net_probe._find_or_post_port(ports, local_port, mmethod)

        expected = "failed"
        self.assertEqual(ret, expected)

    def test_get_interface_subjects(self):
        blipp.net.netifaces = mock.Mock()
        blipp.net.netifaces.interfaces.return_value = ["wlan0"]
        self.net_probe.get_interfaces_in_unis = mock.Mock()
        self.net_probe._build_port_dict = mock.Mock()
        self.net_probe._build_port_dict.return_value = net_consts.local_port
        self.net_probe._find_or_post_port = mock.Mock()
        self.net_probe._find_or_post_port.return_value = "aportref"

        expected = {"wlan0":"aportref"}
        ret = self.net_probe.get_interface_subjects()
        self.assertEqual(expected, ret)

    def test_get_interface_subjects2(self):
        blipp.net.netifaces = mock.Mock()
        blipp.net.netifaces.interfaces.return_value = ["wlan0"]
        self.net_probe.get_interfaces_in_unis = mock.Mock()
        self.net_probe._build_port_dict = mock.Mock()
        self.net_probe._build_port_dict.return_value = net_consts.local_port
        self.net_probe._find_or_post_port = mock.Mock()
        self.net_probe._find_or_post_port.return_value = u'aportref'

        expected = {"wlan0":u'aportref'}
        ret = self.net_probe.get_interface_subjects()
        self.assertEqual(expected, ret)

    def test_get_interface_subjects3(self):
        blipp.net.netifaces = mock.Mock()
        blipp.net.netifaces.interfaces.return_value = ["wlan0"]
        self.net_probe.get_interfaces_in_unis = mock.Mock()
        self.net_probe._build_port_dict = mock.Mock()
        self.net_probe._build_port_dict.return_value = net_consts.local_port
        self.net_probe._find_or_post_port = mock.Mock()
        self.net_probe._find_or_post_port.return_value = 32

        expected = {"wlan0":"unexpected type"}
        ret = self.net_probe.get_interface_subjects()
        self.assertEqual(expected, ret)

