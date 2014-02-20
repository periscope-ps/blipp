import time
import datetime, calendar
import settings
from probe_runner import ProbeRunner
from multiprocessing import Process, Pipe
from copy import copy
from config_server import ConfigServer
import pprint

import subprocess
from utils import merge_into

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
        self._retired = []

    def reload_all(self):
        self.config_obj.refresh()
        self._cleanup_stopped_probes()
        if self.config_obj.get("status", "ON").upper() == "OFF":
            self._stop_all()
            return time.time()
        self._check_procs()
        new_m_list = self.config_obj.get_measurements()
        new_id_list = [x["id"] for x in new_m_list]

        for m in new_m_list:            
            if "scheduled_times" in m:
                if m['id'] not in self._retired:
                    self._start_new_probe(m)
                    self._retired.append(m['id'])
                
            elif "resources" not in m["configuration"]:
                links = [{"ref": "(localhost)"}]
                dst_ip = m["configuration"]["--client"]
                proc = subprocess.Popen(["traceroute", dst_ip], stderr = subprocess.PIPE, stdout = subprocess.PIPE)
                return_code = proc.wait()
        
                for line in proc.stdout:
                    # should improve the robustness of following parsing
                    try:
                        int(line.split()[0])
                        links.append({"ref": line.split()[2]})
                    except ValueError:
                        pass

                for line in proc.stderr:
                    print("stderr: " + line.rstrip())
                    
                m["configuration"]["resources"] = links
                self.config_obj.unis.put("/measurements/"+m["id"], m)
                    
            else:
                pass
                
        for proc_conn, pc in self.proc_to_measurement.iteritems():
            if not pc["id"] in new_id_list:
                if settings.DEBUG:
                    self._print_pc_diff(pc, new_m_list)
                self._stop_probe(proc_conn)
        
        return time.time()

    def _start_new_probe(self, m):
        logger.info("_start_new_probe", name=m["configuration"]["name"])
        logger.debug("_start_new_probe", config=pprint.pformat(m))
        pr = ProbeRunner(self.config_obj, m)
        parent_conn, child_conn = Pipe()
        probe_proc = Process(target = pr.run, args = (child_conn,))
        probe_proc.start()
        self.proc_to_measurement[(probe_proc, parent_conn)] = m

    def _stop_probe(self, proc_conn_tuple):
        try:
            logger.info('_stop_probe',
                        msg="sending stop to " + self.proc_to_measurement[proc_conn_tuple]["configuration"]["name"])
        except Exception:
            logger.info('_stop_probe', msg="sending stop to " + self.proc_to_measurement[proc_conn_tuple]["id"])
        proc_conn_tuple[1].send("stop")
        self.stopped_procs[proc_conn_tuple] = time.time()

    def _stop_all(self):
        '''
        Stop all probes... called when service status is OFF.
        '''
        logger.info('_stop_all')
        for proc, conn in self.proc_to_measurement.keys():
            self._stop_probe((proc, conn))

    def _cleanup_stopped_probes(self):
        '''
        Join probes that were previously stopped, and kill probes that
        should have stopped but didn't.
        '''

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
        '''
        Join probes that have died or exited.
        '''
        for proc, conn in self.proc_to_measurement.keys():
            if not proc.is_alive():
                proc.join()
                logger.warn('_check_procs', msg="a probe has exited", exitcode=proc.exitcode)
                self.proc_to_measurement.pop((proc, conn))

    def _print_pc_diff(self, pc, new_m_list):
        # a helper function for printing the difference between old and new probe configs
        # can be useful for debugging
        for npc in new_m_list:
            if npc["name"] == pc["name"]:
                for key in npc.keys():
                    if key in pc.keys():
                        if not pc[key] == npc[key]:
                            logger.debug("reload_all",
                                         msg=key +
                                         " newval:" +
                                         str(npc[key]) +
                                         " oldval:" + str(pc[key]))
                    else:
                        logger.debug("reload_all", msg="new key/val: " + key + ": " + str(npc[key]))
                for key in pc.keys():
                    if key not in npc.keys():
                        logger.debug("reload_all", msg="deleted key/val: " + key + " :" + str(pc[key]))



def main(config):
    a = Arbiter(config)
    s = ConfigServer(config)
    last_reload_time = time.time()
    check_interval = (float)(config["properties"]["configurations"]["unis_poll_interval"])
    while s.listen(last_reload_time + check_interval - time.time()):
        last_reload_time = a.reload_all()
        check_interval = (float)(config["properties"]["configurations"]["unis_poll_interval"])
        logger.info("main", msg="check interval %d"%check_interval)
