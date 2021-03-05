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
from blipp import settings
import os
import errno
import psutil
from blipp.utils import get_unis

from unis.models import Service

logger = settings.get_logger("registration_probe")

class Probe:
    TTL_DEFAULT = 600
    
    def __init__(self, service, measurement):
        super().__init__(service, measurement)
        self.unis = get_unis()
        self.pname = None
        self.pidfile = None
        self.id = None
        
        try:
            self.serviceType = self.config.service_type
        except Exception:
            logger.error(msg="Must specify service_type!")
            self.serviceType = None

        try:
            self.accessPoint = self.config.service_accesspoint
        except Exception:
            logger.error(msg="Must specify access point!")
            self.accessPoint = None

        try:
            self.pidfile = self.config.pidFile
        except Exception:
            logger.warning(msg="Config does not specify pidfile")
            self.pidfile = None

        self.name = getattr(self.config, 'process_name', None)

        # check for existing service given accessPoint and serviceType
        try:
            self.target = self.unis.services.first_where({'accessPoint': self.accessPoint,
                                                          'serviceType': self.serviceType})
        except Exception as e:
            logger.error(e)

        if self.target is None:
            self.target = self.unis.insert(Service(self._build_service()), commit=True)
            self.unis.flush()

    def get_data(self):
        stat = "UNKNOWN"

        # check pidfile
        if self.pidfile:
            pid = None
            try:
                self.pidfile = open(self.pidfile)
                pid = self.pidfile.read().rstrip()
            except IOError:
                logger.warning(msg="Could not open pidfile: %s" % self.config["pidfile"])
            if pid:
                try:
                    os.kill(int(pid), 0)
                    stat = "ON"
                except OSError as err:
                    if err.errno == errno.ESRCH:
                        stat = "OFF"
                    elif err.errno == errno.EPERM:
                        logger.warning(msg="No permission to signal this process: %s" % pid)
                    else:
                        logger.warn(msg="Uknown error: %s" % error.errno)
                #We could assume if the pidfile exists, the process is running
                #if stat is "UNKNOWN" and os.path.exists("/proc/"+pid):
                #    stat = "ON"
                self.pidfile.close()
        
        # check process name, this takes priority
        if self.pname:
            processes = psutil.process_iter()
            for p in processes:
                if p.name() == self.pname:
                    stat = "ON"
        self.target.status = stat
        self.unis.flush()

        return []

    def _build_service(self):
        service = {
            'serviceType': self.serviceType,
            'description': getattr(self.config, 'service_description', ''),
            'name': getattr(self.config, 'service_name', ''),
            'accessPoint': getattr(self.config, 'service_accesspoint', ''),
            'ttl': getattr(self.config, 'service_ttl', Probe.TTL_DEFAULT),
        }
        try:
            service['runningOn'] = {'href': self.config.service_runningon, 'rel': 'full'}
        except AttributeError:
            service['runningOn'] = self.service.runningOn
        return service
