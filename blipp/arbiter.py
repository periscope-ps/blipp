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
import time
from . import settings
from .probe_runner import ProbeRunner
from multiprocessing import Process, Pipe
from copy import copy
from .config_server import ConfigServer
from blipp.utils import get_unis
import pprint

logger = settings.get_logger('arbiter')
PROBE_GRACE_PERIOD = 10

class Arbiter():
    '''

    The arbiter handles all of the Probes. It reloads the config every
    time the unis poll interval comes around. If new probes have been
    defined or if old probes removed, it starts and stops existing
    probes.

    Each probe is run by the ProbeRunner class in a separate
    subprocess. The arbiter has a dictionary which contains the
    process object for each probe, and the connection object to that
    process. The arbiter can send a "stop" string through the
    connection to give a probe the chance to shut down gracefully. If
    a probe does not shut down within the PROBE_GRACE_PERIOD, it will
    be killed.

    '''

    def __init__(self, config_obj):
        self.config_obj = config_obj # BlippConfigure object
        self.proc_to_measurement = {} # {(proc, conn): measurement_dict, ...}
        self.stopped_procs = {} # {(proc, conn): time_stopped, ...}

    def run_probes(self):
        logger.debug("Starting probes")
        new_m_list = self.config_obj.get_measurements()
        our_m_list = list(self.proc_to_measurement.values())

        get_unis().measurements.addCallback(self._update_probe_callback)

        for m in new_m_list:
            if m.configuration.collection_schedule == 'builtins.scheduled' and \
                not hasattr(m, 'scheduled_times'):
                continue
                
            if settings.DEBUG:
                self._print_pc_diff(m, our_m_list)
            self._start_new_probe(m)

    def reload_all(self):
        self._check_procs()
        interval = self.config_obj.refresh()
        self._cleanup_stopped_probes()
        if self.config_obj.service.status.upper() == "OFF":
            self._stop_all()
        return time.time(), interval

    def _update_probe_callback(self, m, event_type):
        etype = event_type.lower()
        #if etype == "update" or etype == "new" or etype == "delete":
        #    print(etype)
        #    print(m.to_JSON())
        if event_type.lower() == "update" or event_type.lower() == "new":
            logger.debug(f"Updating probe {m.configuration.name}")
            if m.configuration.collection_schedule == 'builtins.scheduled' and \
                not hasattr(m, 'scheduled_times'):
                return
            if settings.DEBUG:
                self._print_pc_diff(m, list(self.proc_to_measurement.values()))
            self._start_new_probe(m)
        if event_type.lower() == "update" or event_type.lower() == "delete":
            for proc_conn, m_old in list(self.proc_to_measurement.items()):
                if m_old.id == m.id:
                    if settings.DEBUG:
                        self._print_pc_diff(m, [m_old])
                    self._stop_probe(proc_conn)
        
    def _start_new_probe(self, m):
        logger.info(f"Starting probe for: {m.configuration.name}")
        logger.debug(pprint.pformat(m.to_JSON()))
        pr = ProbeRunner(self.config_obj.service, m)
        parent_conn, child_conn = Pipe()
        probe_proc = Process(target = pr.run, args = (child_conn,))
        probe_proc.start()
        self.proc_to_measurement[(probe_proc, parent_conn)] = m

    def _stop_probe(self, proc_conn_tuple):
        try:
            logger.info(f"Sending stop signal to {self.proc_to_measurement[proc_conn_tuple].configuration.name}")
        except KeyError:
            logger.info(f"Sending stop signal to {self.proc_to_measurement[proc_conn_tuple].id}")
        proc_conn_tuple[1].send("stop")
        self.stopped_procs[proc_conn_tuple] = time.time()

    def _stop_all(self):
        '''
        Stop all probes... called when service status is OFF.
        '''
        logger.info('_stop_all')
        for proc, conn in list(self.proc_to_measurement.keys()):
            self._stop_probe((proc, conn))

    def _cleanup_stopped_probes(self):
        '''
        Join probes that were previously stopped, and kill probes that
        should have stopped but didn't.
        '''

        now = time.time()
        sp = copy(self.stopped_procs)
        for k,v in list(sp.items()):
            if not k[0].is_alive():
                k[0].join()
                del self.stopped_procs[k]
            elif v < (now - PROBE_GRACE_PERIOD):
                k[0].terminate()
                k[0].join()
                del self.stopped_procs[k]

    def _check_procs(self):
        '''
        Join probes that have died or exited.
        '''
        for proc, conn in list(self.proc_to_measurement.keys()):
            if not proc.is_alive():
                proc.join()
                logger.warn(f"A probe has exited [{proc.exitcode}]")
                m = self.proc_to_measurement.pop((proc, conn))
                m.configuration.status = "OFF"

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
    s = ConfigServer(config)
    last_reload_time = time.time()
    check_interval = int(config.config["properties"]["configurations"]["unis_poll_interval"])
    a.run_probes()
    while s.listen(last_reload_time + check_interval - time.time()):
        last_reload_time, suggested_interval = a.reload_all()
        check_interval = min((float)(config.config["properties"]["configurations"]["unis_max_backoff"]), suggested_interval)
        logger.info(msg="check interval %d"%check_interval)
