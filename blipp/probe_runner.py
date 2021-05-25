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
import time
import socket
from .utils import blipp_import
import pprint
import zmq

HOSTNAME = socket.gethostname()
logger = settings.get_logger('probe_runner')

class ProbeRunner:
    '''
    Class to handle a single probe. Creates the scheduler, collector,
    and probe module associated with this probe. The run method should
    be called as a subprocess (by arbiter) and passed a
    connection object so that it can receive a "stop" if necessary.
    '''

    def __init__(self, service, measurement, sockpath):
        self.measurement = measurement
        self.config = measurement.configuration
        self.service = service
        self.probe_defaults = service.properties.configurations.probe_defaults
        self.setup(sockpath)

    def run(self):
        for nextt in self.scheduler:
            logger.debug(msg="got time from scheduler")
            time.sleep(max(nextt-time.time(), 0))
            self.collect()

    def collect(self):
        logger.debug(f"Collection: '{self.config.name}' from '{self.config.probe_module}'")
        data = self.probe.get_data()
        ts = time.time()
        if data:
            if isinstance(data, list):
                for d in data:
                    msg = bytes(str(self._normalize(d)), "utf8")
                    meas_id = bytes(self.measurement.id, "utf8")
                    self.pub_sock.send_json({'msg': msg.decode('utf8'), 'id': meas_id.decode('utf8')})
            else:
                msg = bytes(str(self._normalize(data)), "utf8")
                meas_id = bytes(self.measurement.id, "utf8")
                self.pub_sock.send_json({'msg': msg.decode('utf8'), 'id': meas_id.decode('utf8')})

    def _normalize(self, data):
        if isinstance(next(iter(data.values())), dict):
            return data
        return dict({self.service.runningOn: data})


    def setup(self, sockpath):
        config = self.config
        logger.info(f"Configuring probe: '{config.name}' running '{config.probe_module}'")
        logger.debug(pprint.pformat(config.to_JSON(top=False)))
        probe_mod = blipp_import(config.probe_module)
        self.probe = probe_mod.Probe(self.service, self.measurement)

        if "." in config.collection_schedule:
            sched_file, sched_name = config.collection_schedule.split('.')
        else:
            sched_file, sched_name = "builtins", config.collection_schedule

        logger.info(f"Using '{sched_file}' on '{sched_name}'")
        self.scheduler = blipp_import("blipp.schedules." + sched_file, fromlist=[1]).__getattribute__(sched_name)
        self.scheduler = self.scheduler(self.service, self.measurement)
        ctx = zmq.Context()
        sock = ctx.socket(zmq.PUB)
        sock.connect(sockpath)
        self.pub_sock = sock
