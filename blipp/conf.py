from unis_client import UNISInstance
import settings
import json
import traceback
from copy import deepcopy
import pprint
from utils import merge_dicts, delete_nones

logger = settings.get_logger('conf')


class ServiceConfigure(object):
    def __init__(self, file_loc=None, unis_url=None, service_id=None,
                 node_id=None, service_name=None, query_service=True):
        self.query_service = query_service
        if not unis_url and not file_loc:
            err_string = \
                "ServiceConfigure initialized with "\
                "neither unis_url nor file_loc"
            raise IncompleteConfigError(err_string)
        self.cmd_cfg = {
            "id": service_id,
            "name": service_name,
            "properties": {
                "configurations": {
                    "unis_url": unis_url,
                    "node_id": node_id,
                    "config_file": file_loc}}}
        delete_nones(self.cmd_cfg)
        self.config = deepcopy(settings.STANDALONE_DEFAULTS)
        merge_dicts(self.config, self.cmd_cfg)

    def refresh_config(self):
        file_cfg = self._get_file_config(
            self.config["properties"]["configurations"].get("config_file", None))
        merge_dicts(self.config, file_cfg)
        merge_dicts(self.config, self.cmd_cfg)
        if self.config["properties"]["configurations"].get("unis_url"):
            self.unis = UNISInstance(self.config)
            self._setup_node()
            self._setup_service()

    def _setup_node(self):
        config = self.config
        logger.debug('_setup_node', config=pprint.pformat(config))
        hostname = config["properties"]["configurations"].get("hostname", None)
        urn = config["properties"]["configurations"].get("host_urn", None)
        node_id = config["properties"]["configurations"].get("node_id", None)
        if node_id:
            r = self.unis.get("/nodes/" + str(node_id))
            if not r:
                logger.warn('_setup_node', msg="node id %s not found" % node_id)
                node_id = None
        if not node_id:
            r = self.unis.get("/nodes?urn=" + urn)
            if len(r):
                r = r[0]
                logger.info('_setup_node',
                            msg="found node with our URN and id %s" % r["id"])
            else:
                r = self.unis.post("/nodes",
                              data={
                        "$schema": settings.SCHEMAS["nodes"],
                        "name": hostname,
                        "urn": urn})

        config["properties"]["configurations"]["node_id"] = r["id"]
        config["runningOn"] = {
            "href": r["selfRef"],
            "rel": "full"}

    def _setup_service(self):
        config = self.config
        logger.debug('_setup_service', config=pprint.pformat(config))
        r = None
        if config.get("id", None):
            r = self.unis.get("/services/" + config["id"])
        if not r and self.query_service:
            logger.warn('_setup_service',
                        msg="service id not specified or not found "\
                            "unis instance ...querying for service")
            rlist = self.unis.get("/services?name=" + config.get("name", None) +
                                      "&runningOn.href=" +
                                  config["runningOn"]["href"] + "&limit=2")
            # loop over the returned services and find one that
            # doesn't return 410 see
            # https://uisapp2.iu.edu/jira-prd/browse/GEMINI-98
            for i in range(len(rlist)):
                r = self.unis.get('/services/' + rlist[i]["id"])
                if r:
                    if isinstance(r, list):
                        logger.warn('_setup_service', msg="id not unique... taking first result")
                        r = r[0]
                    config["id"] = r["id"]
                    logger.info('_setup_service',
                                msg="%s service found with id %s" %\
                                    (config["name"], r["id"]))
                    break
        if not r:
            logger.warn('_setup_service',
                        msg="no service found by id or querying "\
                            "...creating new service")
            r = self.unis.post("/services", data=config)
            merge_dicts(config, r)
        if isinstance(r, list):
            logger.warn('_setup_service', msg="id not unique... taking first result")
            r = r[0]
        merge_dicts(config, r)
        if config != r:
            logger.info("_setup_service", msg="local config changed... pushing new config to UNIS")
            self.unis.put("/services/" + config["id"], data=config)

    def _get_file_config(self, filepath):
        try:
            with open(filepath) as f:
                conf = f.read()
                return json.loads(conf)
        except Exception as e:
            logger.error('_get_file_config', error=str(e), file_name=filepath)
            logger.debug('_get_file_config', trace=traceback.format_exc())
            return {}

    def get(self, key, default=None):
        try:
            return self.config[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        return self.config[key]


class IncompleteConfigError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)
