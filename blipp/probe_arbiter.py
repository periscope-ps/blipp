import time
import settings
from probe_runner import ProbeRunner
from multiprocessing import Process, Pipe
from copy import copy
from config_server import ConfigServer

logger = settings.get_logger('probe_arbiter')
PROBE_GRACE_PERIOD = 10

class Arbiter():
    def __init__(self, config):
        self.config = config # BlippConfigure object
        self.proc_to_config = {} # {(proc, conn): probe_config_dict, ...}
        self.stopped_procs = {} # {(proc, conn): time_stopped, ...}

    def reload_all(self):
        self.config.refresh_config()
        self._cleanup_stopped_probes()
        if self.config.get("status", "ON").upper() == "OFF":
            self._stop_all()
            return time.time()
        self._check_procs()
        new_pc_list = self.config.expand_probe_config()
        our_pc_list = self.proc_to_config.values()
        for pc in new_pc_list:
            if not pc in our_pc_list:
                self._start_new_probe(pc)

        for proc_conn, pc in self.proc_to_config.iteritems():
            if not pc in new_pc_list:
                self._stop_probe(proc_conn)
        return time.time()

    def _start_new_probe(self, pc):
        pr = ProbeRunner(pc)
        parent_conn, child_conn = Pipe()
        probe_proc = Process(target = pr.run, args = (child_conn,))
        probe_proc.start()
        self.proc_to_config[(probe_proc, parent_conn)] = pc

    def _stop_probe(self, proc_conn_tuple):
        proc_conn_tuple[1].send("stop")
        self.stopped_procs[proc_conn_tuple] = time.time()

    def _stop_all(self):
        logger.info('_stop_all')
        for proc, conn in self.proc_to_config.keys():
            self._stop_probe((proc, conn))

    def _cleanup_stopped_probes(self):
        now = time.time()
        sp = copy(self.stopped_procs)
        for k,v in sp.iteritems():
            if not k[0].is_alive():
                k[0].join()
                del self.stopped_procs[k]
            elif v < (now - PROBE_GRACE_PERIOD):
                k[0].terminate()
                k[0].join()
                del self.stopped_procs[k]

    def _check_procs(self):
        for proc, conn in self.proc_to_config.keys():
            if not proc.is_alive():
                proc.join()
                logger.warn('_check_procs', msg="a probe has exited", exitcode=proc.exitcode)
                self.proc_to_config.pop((proc, conn))


def main(config):
    a = Arbiter(config)
    s = ConfigServer(config)
    last_reload_time = 0
    check_interval = config["properties"]["configurations"]["unis_poll_interval"]
    while s.listen(last_reload_time + check_interval - time.time()):
        last_reload_time = a.reload_all()
        check_interval = config["properties"]["configurations"]["unis_poll_interval"]
        logger.info("main", msg="check interval %d"%check_interval)
