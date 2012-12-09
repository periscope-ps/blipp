import time
import settings
from probe_runner import ProbeRunner
from multiprocessing import Process, Pipe
from schedules.builtins import simple

logger = settings.get_logger('probe_arbiter')


class Arbiter():
    def __init__(self, config):
        self.config = config
        self.proc_to_config = {}
        self.stopped_procs = {}

    def reload_all(self):
        self.config.refresh_config()
        self.check_procs()
        new_pc_list = self.config.expand_probe_config()
        our_pc_list = self.proc_to_config.values()
        for pc in new_pc_list:
            if not pc in our_pc_list:
                self.start_new_probe(pc)

        for proc_conn, pc in self.proc_to_config.iteritems():
            if not pc in new_pc_list:
                self.stop_probe(proc_conn)

    def cleanup_stopped(self):
        for k,v in self.stopped_procs.iteritems():
            if k[0].is_alive():
                logger.warn('cleanup_stopped', probe=v.get("name", v))

    def start_new_probe(self, pc):
        pr = ProbeRunner(pc)
        parent_conn, child_conn = Pipe()
        probe_proc = Process(target = pr.run, args = (child_conn,))
        probe_proc.start()
        self.proc_to_config[(probe_proc, parent_conn)] = pc

    def stop_probe(self, proc_conn):
        proc_conn[1].send("stop")
        self.stopped_procs[proc_conn] = self.proc_to_config.pop(proc_conn)

    def check_procs(self):
        for proc, conn in self.proc_to_config.keys():
            if not proc.is_alive():
                logger.warn('check_procs', msg="a probe has exited", exitcode=proc.exitcode)
                self.proc_to_config.pop((proc, conn))


def main(config):
    a = Arbiter(config)
    check_interval = config["properties"]["configurations"]["unis_poll_interval"]
    for x in simple(check_interval):
        a.reload_all()
        time.sleep(max(x-time.time(), 1)) # can't check more than once/second


