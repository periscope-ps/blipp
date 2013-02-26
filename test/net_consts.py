node1 = {
    "$schema": "http://unis.incntre.iu.edu/schema/20120709/node#",
    "name": "VM-4",
    "selfRef": "https://unis.incntre.iu.edu:8443/nodes/VM-4.gemslice4.emulab-net.uky.emulab.net",
    "urn": "urn:publicid:IDN+emulab.net+slice+gemslice4+node+VM-4",
    "ts": 1361831743675539,
    "relations": {
        "over": [
            {
                "href": "urn:publicid:IDN+uky.emulab.net+node+pc73",
                "rel": "full"
                }
            ]
        },
    "properties": {
        "geni": {
            "exclusive": False,
        "component_id": "urn:publicid:IDN+uky.emulab.net+node+pc73",
        "slice_urn": "urn:publicid:IDN+emulab.net+slice+gemslice4",
        "slice_uuid": "58665b24-6b2a-11e2-a39d-001143e453fe",
        "sliver_id": "urn:publicid:IDN+uky.emulab.net+sliver+65601",
        "gemini": {
          "type": "mp_node"
        },
        "hosts": [
          {
            "hostname": "VM-4.gemslice4.emulab-net.uky.emulab.net"
          }
        ],
        "client_id": "VM-4",
        "sliver_type": {
          "name": "emulab-openvz"
        },
        "component_manager_id": "urn:publicid:IDN+uky.emulab.net+authority+cm"
      }
    },
    "location": {
      "latitude": 38.039828,
      "country": "USA",
      "longitude": -84.498013999999998
    },
    "id": "VM-4.gemslice4.emulab-net.uky.emulab.net",
    "ports": [
      {
        "href": "https://unis.incntre.iu.edu:8443/ports/emulab.net_slice_gemslice4_interface_VM-4%3Aif0",
        "rel": "full"
      },
      {
        "href": "https://unis.incntre.iu.edu:8443/ports/emulab.net_slice_gemslice4_interface_VM-4%3Aif1",
        "rel": "full"
      },
      {
        "href": "https://unis.incntre.iu.edu:8443/ports/emulab.net_slice_gemslice4_interface_VM-4%3Aif2",
        "rel": "full"
      }
    ]
  }

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

dev_string = ''' face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    lo:16437577  120248    0    0    0     0          0         0 16437577  120248    0    0    0     0       0          0
  eth0:12267757  166430    0    0    0     0          0      2832 30458998  143263    0    0    0     0       0          0
 wlan0:5029574829 7333434    0    0    0     0          0         0 887097774 4036590    0    0    0     0       0          0
  pan0:       0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
'''

port1 = {
  "$schema": "http://unis.incntre.iu.edu/schema/20120709/port#",
  "name": "VM-4:if0",
  "selfRef": "https://unis.incntre.iu.edu:8443/ports/emulab.net_slice_gemslice4_interface_VM-4:if0",
  "urn": "urn:publicid:IDN+emulab.net+slice+gemslice4+interface+VM-4:if0",
  "ts": 1361831563611036,
  "relations": {
    "over": [
      {
        "href": "urn:publicid:IDN+uky.emulab.net+interface+pc73:lo0",
        "rel": "full"
      }
    ]
  },
  "properties": {
    "geni": {
      "component_id": "urn:publicid:IDN+uky.emulab.net+interface+pc73:lo0",
      "ip": {
        "type": "ipv4",
        "address": "10.128.1.2"
      },
      "slice_urn": "urn:publicid:IDN+emulab.net+slice+gemslice4",
      "slice_uuid": "58665b24-6b2a-11e2-a39d-001143e453fe",
      "sliver_id": "urn:publicid:IDN+uky.emulab.net+sliver+65605",
      "client_id": "VM-4:if0",
      "mac_address": "00000a800102"
    }
  },
  "address": {
    "type": "ipv4",
    "address": "10.128.1.2"
  },
  "id": "emulab.net_slice_gemslice4_interface_VM-4:if0"
}

local_port = {u'$schema': u'http://unis.incntre.iu.edu/schema/20120709/port#',
              u'capacity': -42,
              u'location': {},
              u'name': u'wlan0',
              u'nodeRef': u'urn:ogf:network:domain=hikerbear:node=hikerbear',
              u'properties': {u'ipv4': {u'address': u'192.168.1.88', u'type': u'ipv4'},
                              u'ipv6': {u'address': u'fe80::224:d7ff:fe39:8a64%wlan0',
                                        u'type': u'ipv6'},
                              u'mac': {u'address': u'00:24:d7:39:8a:64', u'type': u'mac'}},
              u'urn': u'urn:ogf:network:domain=hikerbear:node=hikerbear:port=wlan0'}


local_port_resp = {
  "capacity": -42,
  "name": "wlan0",
  "selfRef": "http://dev.incntre.iu.edu/ports/512bee81e77989124d0005f4",
  "urn": "urn:ogf:network:domain=hikerbear:node=hikerbear:port=wlan0",
  "ts": 1361833601555044,
  "id": "512bee81e77989124d0005f4",
  "location": {},
  "$schema": "http://unis.incntre.iu.edu/schema/20120709/port#",
  "nodeRef": "urn:ogf:network:domain=hikerbear:node=hikerbear",
  "properties": {
    "mac": {
      "type": "mac",
      "address": "00:24:d7:39:8a:64"
    },
    "ipv4": {
      "type": "ipv4",
      "address": "192.168.1.88"
    },
    "ipv6": {
      "type": "ipv6",
      "address": "fe80::224:d7ff:fe39:8a64%wlan0"
    }
  }
}
