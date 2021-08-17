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
import time, pprint, zmq, os, json
from . import settings
from .probe_runner import ProbeRunner
from .collector import Collector
from .utils import blipp_import
from multiprocessing import Process, Lock, Event
from copy import copy
from .config_server import ConfigServer
from blipp.utils import get_unis
from unis.models import Measurement, Service

logger = settings.get_logger('arbiter')

class Arbiter():
    '''

    The Arbiter handles all of the Probes. It reloads the config every
    time the update callback function is called from unis. If new probes
    have been defined or if old probes have been removed, it changes the
    priority queue in the scheduler as necessary.

    Each probe is run by the ProbeRunner class in separate processes that
    form a process pool of a configurable size. A process created by the
    Arbiter handles scheduling of measurements through a priority queue
    ordered by next scheduled measurement time. When the scheduled time
    arrives, the Arbiter sends the relevant measurement and service
    information to an idle ProbeRunner process over zmq interprocess
    communication. The Arbiter's main thread then receives data from the
    ProbeRunner and uses a Collector to report the data to unis.

    '''

    def __init__(self, config_obj):
        self.config_obj = config_obj # BlippConfigure object
        self.active_probes = [] # active_probes is mostly used to index 
        self.schedulers = []        #schedulers
        self.addlist = [] # addlist and remlist are used in the scheduler for
        self.remlist = [] #     adding and removing active probes
        self.prioq = [] # Priority queue for schedule. [(delay, m), ...]
        self.id_to_measurement = {} # {id: measurement_dict, ...}
        self.sockpath = self.config_obj.zmqportpath
        self.numprprocs = self.config_obj.numprprocs
        self.sub_sock = self._create_sub_sock()
        self.collector = Collector()
        self.probes_lock = Lock()
        self.sched_interrupt = Event()
        self.free_prprocs = [] # List of IDs of ProbeRunners not currently
                                # getting a measurement

    def start_probes(self):
        logger.debug("Starting probes")
        for i in range(self.numprprocs):
            pr = ProbeRunner(self.sockpath)
            probe_proc = Process(target = pr.run)
            probe_proc.start()
            self.free_prprocs.append(probe_proc.pid)
        new_m_list = self.config_obj.get_measurements()
        get_unis().measurements.addCallback(self._update_probe_callback)
        for m in new_m_list:
            if m.configuration.collection_schedule == 'builtins.scheduled' and \
                not hasattr(m, 'scheduled_times'):
                continue
            if settings.DEBUG:
                self._print_pc_diff(m, new_m_list)
            self.active_probes = []
            self._start_new_probe(m)

    def schedule(self):
        self.pub_sock = self._create_pub_sock()
        self.probes_lock.acquire()
        self._resched()
        self.probes_lock.release()
        while True:
            if len(self.prioq) == 0:
                break
            self.probes_lock.acquire()
            index = 0
            val = self.prioq[0][0]
            for i in range(1, len(self.prioq)):
                if self.prioq[i][0] == val:
                    index += 1
                else:
                    break
            self.probes_lock.release()
            num_meas_next = index+1
            wait_time = max(val-time.time(), 0)
            if wait_time > 0:
                self.sched_interrupt.wait(max(val-time.time(), 0))
            self.probes_lock.acquire()
            if self.sched_interrupt.is_set():
                self.sched_interrupt.clear()
                self._resched()
                continue
            for i in range(num_meas_next):
                m = self.prioq[0][1]
                self._get_measurement(m)
                index = self.active_probes.index(m)
                self.prioq.pop(0)
                self.prioq.append((next(self.schedulers[index]), m))
            self.prioq.sort(reverse=False)
            self.probes_lock.release()

    def _resched(self):
        # Reschedules after a change in configuration. Rescheduling after a
        #   scheduled measurement is handled in scheduler()
        prioq_m = [i[1] for i in self.prioq]
        for m in self.remlist:
            index = prioq_m.index(m)
            self.prioq.pop(index)
            index = active_probes.index(m)
            self.schedulers.pop(index)
            self.active_probes.remove(m)
        self.remlist = []
        for m in self.addlist:
            conf_sched = m.configuration.collection_schedule
            if "." in conf_sched:
                sched_file, sched_name = conf_sched.split('.')
            else:
                sched_file, sched_name = "builtins", conf_sched
            scheduler = blipp_import("blipp.schedules." + sched_file, fromlist=[1]).__getattribute__(sched_name)
            scheduler = scheduler(self.config_obj.service, m)
            self.schedulers.append(scheduler)
            self.active_probes.append(m)
            prioq_tuple = (next(self.schedulers[-1]), m)
            self.prioq.append(prioq_tuple)
        self.addlist = []
        self.prioq.sort(reverse=False)

    def _get_measurement(self, m):
        probe_id = bytes(str(self.free_prprocs.pop(0)), "utf8")
        meas = json.dumps(m.to_JSON())
        service = json.dumps(self.config_obj.service.to_JSON())
        self.pub_sock.send_json({"pr_id": probe_id.decode("utf8"), "measurement": meas, "service": service})
        logger.debug(f"Arbiter has requested {m.configuration.name} data")

    def _create_sub_sock(self):
        ctx = zmq.Context()
        sock = ctx.socket(zmq.SUB)
        sock.setsockopt(zmq.SUBSCRIBE, b"")
        if not(os.path.isdir(self.sockpath)):
            os.mkdir(self.sockpath)
        sock.bind(f"ipc://{self.sockpath}/0")
        return sock

    def _create_pub_sock(self):
        ctx = zmq.Context()
        sock = ctx.socket(zmq.PUB)
        sock.bind(f"ipc://{self.sockpath}/1")
        return sock

    def _update_probe_callback(self, m, event_type):
        etype = event_type.lower()
        if etype == "update" or etype == "new":
            logger.debug(f"Updating probe {m.configuration.name}")
            if m.configuration.collection_schedule == 'builtins.scheduled' and \
                not hasattr(m, 'scheduled_times'):
                return
            if settings.DEBUG:
                self._print_pc_diff(m, active_probes)
            self._start_new_probe(m)
        if etype == "update" or etype == "delete":
            for m_old in self.active_probes:
                if m_old.id == m.id:
                    if settings.DEBUG:
                        self._print_pc_diff(m, [m_old])
                    self._stop_probe(m_old)
        else:
            return
        self.sched_interrupt.set()
        
    def _start_new_probe(self, m):
        logger.info(f"Adding probe for: {m.configuration.name}")
        logger.debug(f"Measurement: \n{pprint.pformat(m.to_JSON())}")
        self.id_to_measurement[m.id] = m
        self.probes_lock.acquire()
        self.addlist.append(m)
        self.probes_lock.release()

    def _stop_probe(self, m):
        try:
            logger.info(f"Stopping {m.configuration.name}")
        except KeyError:
            logger.info(f"Stopping {m.id}")
        self.probes_lock.acquire()
        self.remlist.append(m)
        self.probes_lock.release()

    def _stop_all(self):
        '''
        Stop all probes... called when service status is OFF.
        '''
        logger.info('_stop_all')
        for m in self.active_probes:
            self._stop_probe(m)

    def _print_pc_diff(self, pc, new_m_list):
        # a helper function for printing the difference between old and new probe configs
        # can be useful for debugging
        for npc in new_m_list:
            try:
                if npc.configuration.name == pc.configuration.name:
                    for k,v in npc.to_JSON().items():
                        if getattr(pc, k, object()) != v:
                            logger.debug(f"Updated measurement [{npc.selfRef}]: {getattr(pc, k, None)} -> {getattr(npc, k, None)}")
            except AttributeError:
                logger.debug(msg="name not set")

def main(config):
    a = Arbiter(config)
    a.start_probes()
    meas_sched = Process(target = a.schedule)
    meas_sched.start()
    while True:
        msg = a.sub_sock.recv_json()
        logger.debug(f"Arbiter received from probes: {msg}")
        data = json.loads(msg['msg'])
        m = a.id_to_measurement[msg['id']]
        a.collector.insert(data, m, time.time())
        logger.debug("Collector insert returned")
        a.free_prprocs.append(int(msg['pr']))




