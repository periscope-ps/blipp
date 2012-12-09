import settings
from gemini_client import GeminiClient
from utils import reconcile_config
from copy import deepcopy

logger = settings.get_logger('unis_client')

class UNISInstance:
    def __init__(self, config):
        if not "unis_url" in config: #it's a full service config - not a probe config
            confignoprops = deepcopy(config)
            del confignoprops["properties"]["configurations"]
            config = reconcile_config(confignoprops, config["properties"]["configurations"])
        self.config = config
        unis_url=config['unis_url']
        if unis_url and unis_url[-1]=="/":
            unis_url = unis_url[:-1]
        self.gc = GeminiClient(config, unis_url)

    def post(self, url, data={}):
        return self.gc.do_req('post', url, data)

    def get(self, url, data=None):
        return self.gc.do_req('get', url, data)

    def delete(self, url, data=None):
        return self.gc.do_req('delete', url, data)

    def put(self, url, data=None):
        if "ts" in data:
            del data["ts"]
        return self.gc.do_req('put', url, data)

    def post_metadata(self, subject, metric, config):
        post_dict = {
            "$schema": settings.SCHEMAS["metadata"],
            "subject": {
                "href": subject,
                "rel": "full"
                },
            "eventType":metric,
            "parameters": {
                "datumSchema": settings.SCHEMAS["datum"],
                "config": config
                }
            }
        return self.gc.do_req("post", "/metadata", data=post_dict)

    def post_port(self, post_dict, headers=None):
        ### This should probably update the node to have these ports as well
        if "$schema" not in post_dict:
            post_dict.update({"$schema":settings.SCHEMAS['ports']})
        if "urn" not in post_dict:
            post_dict.update({"urn":settings.URN_STRING + "port=" + \
                              post_dict.get("name", "")})
        if "location" not in post_dict:
            post_dict.update({"location": self.config["location"]})
        return self.gc.do_req("post", "/ports", data=post_dict)
