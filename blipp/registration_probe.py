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
import settings
import os
import errno
import psutil
from unis_client import UNISInstance

logger = settings.get_logger("registration_probe")

class Probe:
    def __init__(self, service, measurement):
        self.config = measurement["configuration"]
        self.service = service
        self.unis = UNISInstance(service)
        self.pname = None
        self.pidfile = None
        self.id = None
        
        try:
            self.serviceType = self.config["service_type"]
        except Exception:
            logger.error("__init__", msg="Must specify service_type!")

        try:
            self.pidfile = self.config.get("pidfile", None)
        except Exception:
            logger.warn("__init__", msg="Config does not specify pidfile")

        self.pname = self.config.get("process_name", None)
        #self.et_string = "ps:tools:blipp:netlogger:"

    def get_data(self):
        stat = "UNKNOWN"

        # check pidfile
        if self.pidfile:
            pid = None
            try:
                self.pidfile = open(self.config["pidfile"])
                pid = self.pidfile.read().rstrip()
            except IOError:
                logger.warn("__init__", msg="Could not open pidfile: %s" % self.config["pidfile"])
            if pid:
                try:
                    os.kill(int(pid), 0)
                    stat = "ON"
                except OSError, err:
                    if err.errno == errno.ESRCH:
                        stat = "OFF"
                    elif err.errno == errno.EPERM:
                        logger.warn("get_data", msg="No permission to signal this process: %s" % pid)
                    else:
                        logger.warn("get_data", msg="Uknown error: %s" % error.errno)
                #We could assume if the pidfile exists, the process is running
                #if stat is "UNKNOWN" and os.path.exists("/proc/"+pid):
                #    stat = "ON"
                self.pidfile.close()
        
        # check process name, this takes priority
        if self.pname:
            processes = psutil.process_iter()
            for p in processes:
                if p.name == self.pname:
                    stat = "ON"

        self.send_service(status=stat)

        return []

    def send_service(self, status="UNKNOWN"):
        service_desc = dict()
        service_desc.update({"$schema": settings.SCHEMAS["services"]})
        service_desc.update({"serviceType": self.serviceType})
        service_desc.update({"status": status})

        try:
            service_desc.update({"description": self.config["service_description"]})
        except:
            pass
        try:
            service_desc.update({"name": self.config["service_name"]})
        except:
            pass
        try:
            service_desc.update({"accessPoint": self.config["service_accesspoint"]})
        except:
            pass
        try:
            service_desc.update({"runningOn": {"href": self.config["service_runningon"],
                                               "rel": "full"}})
        except:
            service_desc.update({"runningOn": {"href": self.service["runningOn"]["href"],
                                               "rel": "full"}})

        if not self.id:
            ret = self.unis.post("/services", service_desc)
            self.id = ret["id"]
        else:
            self.unis.put("/services/"+self.id, service_desc)
        
        
