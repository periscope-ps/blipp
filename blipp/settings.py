import ConfigParser
import socket

SCHEMAS = {
    'networkresources': 'http://unis.incntre.iu.edu/schema/20120709/networkresource#',
    'nodes': 'http://unis.incntre.iu.edu/schema/20120709/node#',
    'domains': 'http://unis.incntre.iu.edu/schema/20120709/domain#',
    'ports': 'http://unis.incntre.iu.edu/schema/20120709/port#',
    'links': 'http://unis.incntre.iu.edu/schema/20120709/link#',
    'paths': 'http://unis.incntre.iu.edu/schema/20120709/path#',
    'networks': 'http://unis.incntre.iu.edu/schema/20120709/network#',
    'topologies': 'http://unis.incntre.iu.edu/schema/20120709/topology#',
    'services': 'http://unis.incntre.iu.edu/schema/20120709/service#',
    'blipp': 'http://unis.incntre.iu.edu/schema/20120709/blipp#',
    'metadata': 'http://unis.incntre.iu.edu/schema/20120709/metadata#',
    'datum': 'http://unis.incntre.iu.edu/schema/20120709/datum#',
    'data': 'http://unis.incntre.iu.edu/schema/20120709/data#'
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

HOSTNAME = socket.gethostname() ### this needs to get the fqdn for DOMAIN to be right down below
NODE_INFO_FILE="/usr/local/etc/node.info"

try:
    DOMAIN = HOSTNAME.split('.', 1)[1]
except Exception:
    DOMAIN = HOSTNAME
HOST_URN = "urn:ogf:network:domain=" + DOMAIN + ":node=" + HOSTNAME.split('.', 1)[0] + ":"

STANDALONE_DEFAULTS = {
    "$schema": SCHEMAS["services"],
    "status": "ON",
    "serviceType": "http://some_schema_domain/blipp",
    "properties": {
        "configurations": {
            "unis_poll_interval":300,
            "use_ssl": "",
	    "ssl_cafile": "",
            "probe_defaults": {
                "collection_schedule": "builtins.simple",
                "schedule_params": {"every": 2}, # run every 2 seconds
                "collection_size": 10000000, # ~10 megabytes
                "collection_ttl": 1500000, # ~17 days
                "reporting_params": 1 # report every probe (no default aggregation)
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
except IOError:
    pass

if AUTH_UUID:
    STANDALONE_DEFAULTS["properties"].update({"geni": {"slice_uuid":AUTH_UUID}})
if MS_URL:
    STANDALONE_DEFAULTS["properties"]["configurations"]["probe_defaults"].update({"ms_url":MS_URL})

##################################################################
# Netlogger stuff... pasted from Ahmed's peri-tornado
##################################################################
import logging
from netlogger import nllog

DEBUG = True
TRACE = False
NETLOGGER_NAMESPACE = "blipp"

def config_logger():
    """Configures netlogger"""
    nllog.PROJECT_NAMESPACE = NETLOGGER_NAMESPACE
    #logging.setLoggerClass(nllog.PrettyBPLogger)
    logging.setLoggerClass(nllog.BPLogger)
    log = logging.getLogger(nllog.PROJECT_NAMESPACE)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(handler)
    # set level
    if TRACE:
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                     nllog.TRACE)[3]
    elif DEBUG:
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                     nllog.TRACE)[2]

    else:
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                     nllog.TRACE)[1]
    log.setLevel(log_level)


def get_logger(namespace=NETLOGGER_NAMESPACE):
    """Return logger object"""
    # Test if netlogger is initialized
    if nllog.PROJECT_NAMESPACE != NETLOGGER_NAMESPACE:
        config_logger()
    return nllog.get_logger(namespace)

##################################################################
# Read in a configuration file
##################################################################

CONFIG_FILE="/etc/periscope/blippd.conf"

config = ConfigParser.RawConfigParser()
config.read(CONFIG_FILE)

main_config = ["unis_url", "ms_url", "ssl_cert", "ssl_key", "ssl_cafile", "unis_poll_interval"]
probe_map = {"registration_probe": ["service_type", "service_name", "service_description", "service_accesspoint", "pidfile"],
             "some other probe": ["blah", "blah2"]}

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
    if module in probe_map.keys():
        conf = dict()
        conf.update({"probe_module": module})
        # set the schedule interval if present (otherwise will get probe default)
        try:
            conf.update({"schedule_params": {"every": (int)(config.get(section, "schedule"))}})
        except:
            pass
        for key in probe_map[module]:
            try:
                value = config.get(section, key)
                conf.update({key: value})
            except:
                pass
        STANDALONE_DEFAULTS["properties"]["configurations"]["probes"].update({section: conf})
