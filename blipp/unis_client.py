import settings
from utils import query_string_from_dict
import urllib
from periscope_client import PeriscopeClient

logger = settings.get_logger('unis_client')

class UNISInstance:
    def __init__(self, service_entry):
        self.service_entry = service_entry
        self.config = service_entry["properties"]["configurations"]
        unis_url=self.config["unis_url"]
        if unis_url and unis_url[-1]=="/":
            unis_url = unis_url[:-1]
        self.pc = PeriscopeClient(service_entry, unis_url)
        self.meas_to_mds = {}

    def post(self, url, data={}):
        return self.pc.do_req('post', url, data)

    def get(self, url, data=None):
        return self.pc.do_req('get', url, data)

    def delete(self, url, data=None):
        return self.pc.do_req('delete', url, data)

    def put(self, url, data=None):
        if "ts" in data:
            del data["ts"]
        return self.pc.do_req('put', url, data)

    def find_or_create_metadata(self, subject, metric, measurement):
        if not measurement["id"] in self.meas_to_mds:
            mds = self.get("/metadata?parameters.measurement.href=" + measurement["selfRef"])
            if mds:
                self.meas_to_mds[measurement["id"]] = mds
        mds = self.meas_to_mds.get(measurement["id"], [])
        for md in mds:
            if md["subject"] == subject and md["eventType"] == metric:
                return md

        post_dict = {
            "$schema": settings.SCHEMAS["metadata"],
            "subject": {
                "href": subject,
                "rel": "full"
            },
            "eventType": metric,
            "parameters": {
                "datumSchema": settings.SCHEMAS["datum"],
                "measurement": {
                    "href": measurement["selfRef"],
                    "rel": "full"
                }
            }
        }
        return self.pc.do_req("post", "/metadata", data=post_dict)

    def post_port(self, post_dict, headers=None):
        if "$schema" not in post_dict:
            post_dict.update({"$schema":settings.SCHEMAS['ports']})
        if "urn" not in post_dict:
            post_dict.update({"urn":settings.HOST_URN + "port=" + \
                              post_dict.get("name", "")})
        if "location" not in post_dict and "location" in self.config:
            post_dict.update({"location": self.config["location"]})
        port_post = self.pc.do_req("post", "/ports", data=post_dict)
        # Update the node to have these ports as well
        if port_post:
            node_rep = self.get_node()
            node_rep.setdefault("ports", []).append({"href":port_post["selfRef"],
                                                     "rel": "full"})
            self.put(node_rep["selfRef"], data=node_rep)
        return port_post

    def get_node(self, config=None):
        if not config:
            config = self.config
        node_url = config['runningOn']['href']
        return self.get(node_url)
