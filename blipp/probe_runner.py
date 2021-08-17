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
from . import settings
import time, socket, pprint, zmq, os, json
from .utils import blipp_import
from blipp.utils import get_unis
from unis.models import Service, Measurement

HOSTNAME = socket.gethostname()
logger = settings.get_logger('probe_runner')

class ProbeRunner:
    '''
    Class to handle a single probe. A configurable number of probes
    are created upon startup of Blipp and the run method is called
    as a subprocess for each ProbeRunner. The ProbeRunner sits idle
    until it receives service and measurement objects from the arbiter over
    a zmq connection. The ProbeRunner then takes a single measurement,
    sends the data to the Arbiter, and returns to an idle state.
    '''

    def __init__(self, sockpath):
        self.sockpath = sockpath

    def run(self):
        self.pub_sock = self._create_pub_sock(self.sockpath)
        self.sub_sock = self._create_sub_sock(self.sockpath)
        while True:
            msg = self.sub_sock.recv_json()
            if not(int(msg['pr_id']) == os.getpid()):
                continue
            self.measurement = Measurement(json.loads(msg['measurement']))
            logger.debug(f"Probe {os.getpid()} processing {self.measurement.configuration.name} data request")
            self.config = self.measurement.configuration
            service_dict = json.loads(msg['service'])
            self.service = get_unis().services.first_where({'selfRef': service_dict['selfRef']})
            probe_mod = blipp_import(self.config.probe_module)
            self.probe = probe_mod.Probe(self.service, self.measurement)
            self.collect()

    def collect(self):
        logger.debug(f"Collection: '{self.config.name}' from '{self.config.probe_module}'")
        data = self.probe.get_data()
        logger.debug(f"Probe for '{self.measurement.configuration.name}' got data\n{data}")
        ts = time.time()
        if data:
            if isinstance(data, list):
                for d in data:
                    msg = bytes(str(self._normalize(d)), "utf8")
                    meas_id = bytes(self.measurement.id, "utf8")
                    pr_id = bytes(str(os.getpid()), "utf8")
                    self.pub_sock.send_json({'msg': msg.decode('utf8'), 'id': meas_id.decode('utf8'), 'pr': pr_id.decode('utf8')})
            else:
                msg = json.dumps(self._normalize(data))
                meas_id = bytes(self.measurement.id, "utf8")
                pr_id = bytes(str(os.getpid()), "utf8")
                self.pub_sock.send_json({'msg': msg, 'id': meas_id.decode('utf8'), 'pr': pr_id.decode('utf8')})

    def _normalize(self, data):
        if isinstance(next(iter(data.values())), dict):
            return data
        return dict({self.service.runningOn.selfRef: data})

    def _create_sub_sock(self, sockpath):
        ctx = zmq.Context()
        sock = ctx.socket(zmq.SUB)
        sock.setsockopt(zmq.SUBSCRIBE, b"")
        sock.connect(f"ipc://{sockpath}/1")
        return sock

    def _create_pub_sock(self, sockpath):
        ctx = zmq.Context()
        sock = ctx.socket(zmq.PUB)
        sock.connect(f"ipc://{sockpath}/0")
        return sock

