import settings
from gemini_client import GeminiClient
logger = settings.get_logger('ms_client')


class MSInstance:
    def __init__(self, config):
        self.config = config
        self.ms_url=config.get("ms_url", None)
        self.gc = GeminiClient(config, self.ms_url)
        self.mids = set()

    def _def_headers(self, ctype):
        def_headers={'content-type':
                          'application/perfsonar+json profile=' + settings.SCHEMAS[ctype],
                          'accept':"*/*"}
        return def_headers

    def post_events(self, mid, size, ttl):
        data = dict({"metadata_URL": self.ms_url + "/metadata/" + mid,
                     "collection_size": size,
                     "ttl": ttl
                     })
        headers = self._def_headers("datum")
        return self.gc.do_req('post', '/events', data, headers)

    def post_data(self, data):
        mids = [ x["mid"] for x in data ]
        self._check_mids(mids)
        headers = self._def_headers("data")
        return self.gc.do_req('post', '/data', data, headers)

    def _check_mids(self, mids):
        coll_size = self.config["collection_size"]
        coll_ttl = self.config["collection_ttl"]
        for mid in mids:
            if mid not in self.mids:
                if not self.gc.get("/events?mids=" + str(mid)):
                    if self.post_events(mid, coll_size, coll_ttl):
                        self.mids.add(mid)
                else:
                    self.mids.add(mid)
