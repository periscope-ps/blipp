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
import configparser
import socket
import netifaces
from . import utils

SCHEMAS = {
    'networkresources': 'http://unis.crest.iu.edu/schema/20160630/networkresource#',
    'nodes': 'http://unis.crest.iu.edu/schema/20160630/node#',
    'domains': 'http://unis.crest.iu.edu/schema/20160630/domain#',
    'ports': 'http://unis.crest.iu.edu/schema/20160630/port#',
    'links': 'http://unis.crest.iu.edu/schema/20160630/link#',
    'paths': 'http://unis.crest.iu.edu/schema/20160630/path#',
    'networks': 'http://unis.crest.iu.edu/schema/20160630/network#',
    'topologies': 'http://unis.crest.iu.edu/schema/20160630/topology#',
    'services': 'http://unis.crest.iu.edu/schema/20160630/service#',
    'blipp': 'http://unis.crest.iu.edu/schema/20160630/blipp#',
    'metadata': 'http://unis.crest.iu.edu/schema/20160630/metadata#',
    'datum': 'http://unis.crest.iu.edu/schema/20160630/datum#',
    'data': 'http://unis.crest.iu.edu/schema/20160630/data#',
    'measurement': 'http://unis.crest.iu.edu/schema/20160630/measurement#',
    }

MIME = {
    'HTML': 'text/html',
    'JSON': 'application/json',
    'PLAIN': 'text/plain',
    'SSE': 'text/event-stream',
    'PSJSON': 'application/perfsonar+json',
    'PSBSON': 'application/perfsonar+bson',
    'PSXML': 'application/perfsonar+xml',
    }

'''
Calculate URN deterministic way with a goal to make it as unique as
possible. We might still get into situation where urn might not be unique
if appropriate reverse dns entries are not set or duplicate MAC addresses
are used.

We construct urn as follows.
case 1) socket.getfqdn() resolves into monitor.incentre.iu.edu then 
  urn=urn:ogf:network:domain=incentre.iu.edu:node=monitor:
case 2) socket.getgqdn() fails then
  urn=urn:ogf:network:domain=<FQDN>:node=<default_interface_ip>_<mac_address_of_default_interface>_<hostname>:
'''
HOSTNAME = socket.getfqdn() ### this might fail n give hostname
fqdn = socket.getfqdn()
hostname = socket.gethostname()

if not fqdn or not hostname:
    raise Exception("socket.getfqdn or socket.gethostname failed.\
        Try setting urn manually.")

#we check fqdn != hostname, if not then we have success
if fqdn != hostname:
    domain = fqdn.replace(hostname+".", "")
    HOST_URN = "urn:ogf:network:domain=%s:node=%s:" % (domain, hostname)
else:
    try:
        default_ip, default_iface = utils.get_default_gateway_linux()
        default_ip =  netifaces.ifaddresses(default_iface)[netifaces.AF_INET][0]["addr"]
        default_mac = netifaces.ifaddresses(default_iface)[netifaces.AF_LINK][0]["addr"]
        default_mac = utils.clean_mac(default_mac)
        HOST_URN = "urn:ogf:network:domain=%s:node=%s_%s_%s" % \
            (fqdn, default_ip, default_mac, hostname)
    except Exception:
        domain = fqdn.replace(hostname+".", "")
        HOST_URN = "urn:ogf:network:domain=%s:node=%s:" % (domain, hostname)

NODE_INFO_FILE="/usr/local/etc/node.info"

STANDALONE_DEFAULTS = {
    "$schema": SCHEMAS["services"],
    "status": "ON",
    "serviceType": "ps:tools:blipp",
    "ttl": 600,
    "properties": {
        "configurations": {
            "unis_url": "http://localhost:8888",
            "unis_max_backoff": 3600,
            "unis_poll_interval":300,
            "use_ssl": "",
	    "ssl_cafile": "",
            "probe_defaults": {
                "collection_schedule": "builtins.simple",
                "schedule_params": {"every": 2}, # run every 2 seconds
                "collection_size": 10000000,     # ~10 megabytes
                "collection_ttl": 1500000,       # ~17 days
                "reporting_params": 1,           # report every probe (no default aggregation)
                "reporting_tolerance": 10        # store 10 on unreachable MS
            },
            "probes": {
            }
        }
    }
}

nconf = {}
AUTH_UUID = None
UNIS_ID = None
MS_URL = None
GN_ADDR = None
try:
    with open(NODE_INFO_FILE, 'r') as cfile:
        for line in cfile:
            name, var = line.partition("=")[::2]
            nconf[name.strip()] = str(var).rstrip()
        try:
            MS_URL = nconf['ms_instance']
        except Exception as e:
            pass
        try:
            AUTH_UUID = nconf['auth_uuid']
        except Exception as e:
            pass
        try:
            UNIS_ID = nconf['unis_id']
        except Exception as e:
            pass
        try:
            GN_ADDR = nconf['gn_address']
        except Exception as e:
            pass
except IOError:
    pass

if AUTH_UUID:
    STANDALONE_DEFAULTS["properties"].update({"geni": {"slice_uuid":AUTH_UUID}})
if MS_URL:
    STANDALONE_DEFAULTS["properties"]["configurations"]["probe_defaults"].update({"ms_url":MS_URL})

##################################################################
# Netlogger stuff... pasted from Ahmed's peri-tornado
##################################################################
import logging, logging.handlers
#from netlogger import nllog

DEBUG = False
TRACE = False
CONSOLE = True
NETLOGGER_NAMESPACE = "blippd"
WORKSPACE = "."

# 2021-01-29
# Entire logging section commented out and replaced with code section below
# in order to make code translation from Python 2 to Python 3 easier

def get_logger(namespace="blipp", logfile=None, level=None):
    if level is not None:
        levels = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARN': logging.WARN }
        #logging.basicConfig(level=levels.get(level, logging.WARN))
    return logging.getLogger(namespace)

''' 
def config_logger():
    """Configures netlogger"""
    nllog.PROJECT_NAMESPACE = NETLOGGER_NAMESPACE
    #logging.setLoggerClass(nllog.PrettyBPLogger)
    logging.setLoggerClass(nllog.BPLogger)
    log = logging.getLogger(nllog.PROJECT_NAMESPACE)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(handler)
    if GN_ADDR:
        # setup socket to global node, GN
        socketHandler = logging.handlers.SocketHandler(GN_ADDR,
                                                       logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        log.addHandler(socketHandler)
    # set level
    if TRACE:
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                     nllog.TRACE)[3]
    elif DEBUG:
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                     nllog.TRACE)[2]
    elif CONSOLE:	
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                     25)[3]
    else:
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                     nllog.TRACE)[1]
    log.setLevel(log_level)

def add_filehandler(logfile):
    log = logging.getLogger(nllog.PROJECT_NAMESPACE)
    log.handlers = []
    
    try:
        fileHandler = logging.handlers.RotatingFileHandler(logfile, maxBytes = 500000, backupCount = 5)
        fileHandler.setFormatter(logging.Formatter("%(message)s"))
        log.addHandler(fileHandler)
    except  AttributeError as exp:
        log.error("Could not attach File Logger: {exp}".format(exp = exp))

def set_level(level):
    log = logging.getLogger(nllog.PROJECT_NAMESPACE)
    level = level.upper()
    
    if level == 'TRACE':
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                     nllog.TRACE)[3]
    elif level == 'DEBUG':
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                     nllog.TRACE)[2]
    elif level == 'CONSOLE':	
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                     25)[3]
    else:
        return
    
    log.setLevel(log_level)    

def get_logger(namespace=NETLOGGER_NAMESPACE, logfile=None, level=None):
    """Return logger object"""
    # Test if netlogger is initialized
    if nllog.PROJECT_NAMESPACE != NETLOGGER_NAMESPACE:
        config_logger()

    if logfile:
        add_filehandler(logfile)
    if level:
        set_level(level)

    return nllog.get_logger(namespace)
'''

##################################################################
# Read in a configuration file
##################################################################

CONFIG_FILE="/etc/periscope/blippd.conf"

config = configparser.RawConfigParser()
config.read(CONFIG_FILE)

main_config = ["unis_url", "ms_url", "data_file", "ssl_cert", "ssl_key",
               "ssl_cafile", "unis_poll_interval", "use_ssl"]
probe_map = {"registration_probe": ["service_type", "service_name", "service_description",
                                    "service_accesspoint", "pidfile", "process_name",
                                    "service_ttl"],
             "net": ["unis_url"],
             "cpu": ["proc_dir"],
             "mem": []}

for key in main_config:
    try:
        value = config.get("main", key)
        STANDALONE_DEFAULTS["properties"]["configurations"].update({key: value})
    except:
        pass

for section in config.sections():
    if section == "main":
        continue
    module = config.get(section, "module")
    if module in list(probe_map.keys()):
        conf = dict()
        conf.update({"probe_module": module})
        # set the schedule interval if present (otherwise will get probe default)
        try:
            conf.update({"schedule_params": {"every": (int)(config.get(section, "interval"))}})
        except:
            pass
        for key in probe_map[module]:
            try:
                value = config.get(section, key)
                conf.update({key: value})
            except:
                pass
        STANDALONE_DEFAULTS["properties"]["configurations"]["probes"].update({section: conf})
