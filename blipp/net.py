import os
import ethtool
import netifaces
from unis_client import UNISInstance
import settings
from utils import full_event_types, blipp_import_method
import re

logger = settings.get_logger('net')
class Proc:
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

class Probe:
    """Get network statistics
    """
    UNUSED_METRICS = ["errs_in", "errs_out", "drop_in", "drop_out",
                      "fifo_in", "fifo_out", "frame_in", "compressed_in",
                      "compressed_out", "multicast_in", "colls_out", "colls_in",
                      "carrier_out", "carrier_in", "frame_out", "multicast_out"]

    def __init__(self, config={}):
        kwargs = config.get("kwargs", {})
        logger.debug('Probe.__init__', kwargs=str(kwargs))
        self.config = config
        self._proc = Proc(kwargs.get("proc_dir", "/proc/"))
        self.node_subject=kwargs.get("subject", config.get("runningOn", {}).get('href', 'not found'))
        self.port_match_method=kwargs.get("port_match_method", "geni_utils.mac_match")
        self.port_match_method=blipp_import_method(self.port_match_method)
        self.unis = None
        logger.debug('Probe.__init__ ', subject=self.node_subject)
        self.subjects=self.get_interface_subjects()

    def _get_unis(self):
        if not self.unis:
            self.unis = UNISInstance(self.config)
        return self.unis

    def get_data(self):
        netdev = self._proc.open('net', 'dev')
        netsnmp = self._proc.open('net', 'snmp')
        netdev.readline()
        data = self._get_dev_data(netdev.read())
        sdata = self._get_snmp_data(netsnmp.read())

        data[self.node_subject] = sdata
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
            face_data = dict(zip(headers, line))
            self._vals_to_int(face_data)
            errors = face_data.pop('errs_in') + face_data.pop('errs_out')
            drops = face_data.pop('drop_in') + face_data.pop('drop_out')
            face_data['errors'] = errors
            face_data['drops'] = drops
            for metric in self.UNUSED_METRICS:
                if metric in face_data:
                    del face_data[metric]
            data[self.subjects[iface]] = face_data

        return data

    def _vals_to_int(self, adict):
        for k,v in adict.items():
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
            local_port_dict = self._build_port_dict(face)
            portRef = self._find_or_post_port(unis_ports, local_port_dict, self.port_match_method)
            if isinstance(portRef, str) or isinstance(portRef, unicode):
                subjects[face]=portRef
            else:
                logger.warn('get_interface_subjects',
                            msg="subject for face %s is of an unexpected type %s, portRef=%s"%(face,
                                                                                               type(portRef),
                                                                                               portRef))
                subjects[face]="unexpected type"
        return subjects

    def _build_port_dict(self, port_name):
        type_map = {'ipv4': netifaces.AF_INET,
                    'ipv6': netifaces.AF_INET6,
                    'mac': netifaces.AF_LINK}

        post_dict = {}
        try:
            capacity = ethtool.get_speed(port_name)
        except OSError:
            capacity = 0

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
                logger.exc('get_interface_subjects', e)

            # TODO some sort of verification here that capacity is right
        post_dict['name'] = port_name
        post_dict['capacity'] = capacity

            # hack in a 'nodeRef' so we can find port from rspec
        post_dict['nodeRef'] = settings.URN_STRING[:-1]
        return post_dict

    def get_interfaces_in_unis(self):
        node = self._get_unis().get_node()
        port_list = node.get('ports', [])
        ports = []
        for port in port_list:
            ports.append(self._get_unis().get(port['href']))
        return ports

    def _find_or_post_port(self, ports, local_port, matching_method):
        for port in ports:
            if matching_method(port, local_port):
                return port["selfRef"]
        post = self._get_unis().post_port(local_port)
        if post:
            return post["selfRef"]
        else:
            logger.warn('_find_or_post_port',
                        msg="post seems to have failed... subject for %s will be wrong" % local_port['name'])
            return "failed"

