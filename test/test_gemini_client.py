import unittest2
import blipp.gemini_client as bg
from blipp import settings
import mock
import json

class GeminiClientTests(unittest2.TestCase):
    def setUp(self):
        self.gc = bg.GeminiClient({"unis_url": "fakeurl",
                                   "use_ssl": "yes",
                                   "ssl_cert": "/path/cert",
                                   "ssl_key": "/path/key",
                                   "ssl_cafile": "/path/cafile",
                                   "properties":
                                   {"geni":
                                        {"slice_uuid": "testuuid"}}}, "fakeurl")

    def test_url_schema_headers1(self):
        url = "/nodes"
        u, s, h = self.gc._url_schema_headers(url)
        self.assertEqual(u, "fakeurl/nodes")
        self.assertEqual(s, settings.SCHEMAS["nodes"])

    def test_url_schema_headers2(self):
        url = "/nodes/"
        u, s, h = self.gc._url_schema_headers(url)
        self.assertEqual(u, "fakeurl/nodes")
        self.assertEqual(s, settings.SCHEMAS["nodes"])

    def test_url_schema_headers3(self):
        url = "/nodes/dea239804dbeef"
        u, s, h = self.gc._url_schema_headers(url)
        self.assertEqual(u, "fakeurl/nodes/dea239804dbeef")
        self.assertEqual(s, settings.SCHEMAS["nodes"])

    def test_url_schema_headers4(self):
        url = "/nodes?hostname=blarg"
        u, s, h = self.gc._url_schema_headers(url)
        self.assertEqual(u, "fakeurl/nodes?hostname=blarg")
        self.assertEqual(s, settings.SCHEMAS["nodes"])


    def test_do_req(self):
        bg.http = mock.Mock()
        bg.http.make_request.return_value = 1

        self.gc.do_req('post', '/events', {"metadata_URL": "fakeurl/metadata/testmid",
                                      "collection_size": 100,
                                      "ttl": 1000})
        req_data = {"metadata_URL": "fakeurl/metadata/testmid",
                    "collection_size": 100,
                    "ttl": 1000,
                    "properties": {"geni": {"slice_uuid": "testuuid"}}}

        bg.http.make_request.assert_called_with('post', 'fakeurl/events',
                                                None, json.dumps(req_data),
                                                "/path/cert", "/path/key",
                                                "/path/cafile")
