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
import os
from blipp import ethtool
import netifaces
from blipp import settings
from blipp.utils import full_event_types, blipp_import_method, get_unis
from blipp.probes import abc
import re

from unis.models import Node

logger = settings.get_logger('net')
class Proc(abc.Probe):
    """Wrapper to opening files in /proc
    """
    def __init__(self, dirname="/proc"):
        """Initialize with optional alternate dirname.
        """
        self._dir = dirname

    def open(self, *path):
        """Open a given file under proc.
        'path' is a sequence of path components like ('net', 'dev')
        """
        return open(os.path.join(self._dir, *path))

    def exists(self, *path):
        try:
            a = open(os.path.join(self._dir, *path))
            return a
        except IOError:
            return False

EVENT_TYPES={
    "packets_in":"ps:tools:blipp:linux:network:ip:utilization:packets:in",
    "packets_out":"ps:tools:blipp:linux:network:ip:utilization:packets:out",
    "bytes_in":"ps:tools:blipp:linux:network:utilization:bytes:in",
    "bytes_out":"ps:tools:blipp:linux:network:utilization:bytes:out",
    "errors":"ps:tools:blipp:linux:network:ip:utilization:errors",
    "drops":"ps:tools:blipp:linux:network:ip:utilization:drops",
    "tcp_segments_in":"ps:tools:blipp:linux:network:tcp:utilization:segments:in",
    "tcp_segments_out":"ps:tools:blipp:linux:network:tcp:utilization:segments:out",
    "tcp_retrans":"ps:tools:blipp:linux:network:tcp:utilization:retrans",
    "datagrams_in":"ps:tools:blipp:linux:network:udp:utilization:datagrams:in",
    "datagrams_out":"ps:tools:blipp:linux:network:udp:utilization:datagrams:out"
    }

class Probe(abc.Probe):
    """Get network statistics
    """
    UNUSED_METRICS = ["errs_in", "errs_out", "drop_in", "drop_out",
                      "fifo_in", "fifo_out", "frame_in", "compressed_in",
                      "compressed_out", "multicast_in", "colls_out", "colls_in",
                      "carrier_out", "carrier_in", "frame_out", "multicast_out"]

    def __init__(self, service, measurement):
        super().__init__(service, measurement)
        logger.debug(self.config)
        self._proc = Proc(getattr(self.config, 'proc_dir', '/proc/'))
        print("<------------------ The bug is here")
        self.node_subject = getattr(self.config, 'subject', None) or getattr(self.config, 'runningOn', None) or Node()
        self.port_match_method = blipp_import(getattr(self.config, 'port_match_method', 'geni_utils.mac_match'))
        self.unis = get_unis()
        
        logger.debug(f"Probe[net] subject: {self.node_subject.selfRef}")
        self.subjects=self.get_interface_subjects()

    def get_data(self):
        netdev = self._proc.open('net', 'dev')
        netsnmp = self._proc.open('net', 'snmp')
        netdev.readline()
        data = self._get_dev_data(netdev.read())
        sdata = self._get_snmp_data(netsnmp.read())

        data[self.node_subject.selfRef] = sdata
        data = full_event_types(data, EVENT_TYPES)
        return data

    def _get_dev_data(self, dev_string):
        headers_regex = re.compile(
            '[^|]*\|(?P<rxheaders>[^|]*)\|(?P<txheaders>.*)')
        dev_lines = dev_string.splitlines()
        matches = headers_regex.search(dev_lines.pop(0)).groupdict()
        txheaders = [ head + "_in" for head in matches['txheaders'].split() ]
        rxheaders = [ head + "_out" for head in matches['rxheaders'].split() ]
        headers = txheaders + rxheaders
        data = {}
        for line in dev_lines:
            if not line:
                continue
            line = line.replace(':', ' ')
            line = line.split()
            iface = line.pop(0)
            face_data = dict(list(zip(headers, line)))
            self._vals_to_int(face_data)
            errors = face_data.pop('errs_in') + face_data.pop('errs_out')
            drops = face_data.pop('drop_in') + face_data.pop('drop_out')
            face_data['errors'] = errors
            face_data['drops'] = drops
            for metric in self.UNUSED_METRICS:
                if metric in face_data:
                    del face_data[metric]
            data[self.subjects[iface].selfRef] = face_data

        return data

    def _vals_to_int(self, adict):
        for k,v in list(adict.items()):
            adict[k] = int(v)
        return adict

    def _get_snmp_data(self, snmp_string):
        data = {}
        lines = snmp_string.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].split()
            if line[0].lower()=="tcp:":
                i += 1
                in_index      = line.index("InSegs")
                out_index     = line.index("OutSegs")
                retrans_index = line.index("RetransSegs")
                dataline = lines[i].split()
                data.update({"tcp_segments_in":dataline[in_index],
                                     "tcp_segments_out":dataline[out_index],
                                     "tcp_retrans":dataline[retrans_index]})
            elif line[0].lower()=="udp:":
                i += 1
                in_index  = line.index("InDatagrams")
                out_index = line.index("OutDatagrams")
                dataline = lines[i].split()
                data.update({"datagrams_in":dataline[in_index],
                                     "datagrams_out":dataline[out_index]})
            i += 1
        return self._vals_to_int(data)

    def get_interface_subjects(self):
        subjects = {}
        unis_ports = self.get_interfaces_in_unis()

        for face in netifaces.interfaces():
            p = self.node_subject.ports.first_where(lambda x: self.port_match_method(face, x))
            if p is None:
                p = self.unis.insert(Port(self._build_port_dict(face)), commit=True)
                self.node_subject.ports.append(p)
            subjects[face] = p
        self.unis.flush()
        return subjects

    def _build_port_dict(self, port_name):
        type_map = {'ipv4': netifaces.AF_INET,
                    'ipv6': netifaces.AF_INET6,
                    'mac': netifaces.AF_LINK}

        try:
            capacity = ethtool.get_speed(port_name)
        except OSError:
            capacity = 0
        post_dict = {
            'name': port_name,
            'capacity': capacity,
            'nodeRef': settings.HOST_URN[:-1]
        }

            # assume each port is a layer2 port for the main 'address'
        try:
            l2_addr = netifaces.ifaddresses(port_name)[type_map['mac']]
            if len(l2_addr):
                addr = {"type": "mac", "address": l2_addr[0]['addr']}
                post_dict['address'] = addr.strip().replace(':', '').lower()
        except:
            pass

            # add all the other address info we can find
        post_dict['properties'] = {}
        for t in type_map:
            try:
                addrs = netifaces.ifaddresses(port_name)[type_map[t]]
                for a in addrs:
                    addr = {"type": t, "address": a['addr']}
                    post_dict['properties'][t] = addr
            except Exception as e:
                #logger.exc('get_interface_subjects', e)
                # logging.exc appears to be deprecated, as the interpreter
                #   doesn't recognize it
                pass
            # TODO some sort of verification here that capacity is right
        return post_dict

    def get_interfaces_in_unis(self):
        node = self.service.runningOn
        ports = []
        if node:
            port_list = node.get('ports', [])
            for port in port_list:
                p = self.unis.get(port['href'])
                ports.append(p)
        return ports

    def _find_or_post_port(self, ports, local_port, matching_method):
        for port in ports:
            if matching_method(port, local_port):
                return port["selfRef"]
        post = self.unis.post_port(local_port)
        if post:
            return post["selfRef"]
        else:
            logger.warning(msg="post seems to have failed... subject for %s will be wrong" % local_port['name'])
            return "failed"
