import unittest2
from blipp.unis_client import UNISInstance
from blipp import settings

class UNISInstanceTests(unittest2.TestCase):
    def setUp(self):
        self.unis = UNISInstance({"unis_url":"fakeurl"})

    # def test_url_schema_headers1(self):
    #     url = "/nodes"
    #     u, s, h = self.unis._url_schema_headers(url)
    #     self.assertEqual(u, "/nodes")
    #     self.assertEqual(s, settings.SCHEMAS["nodes"])

    # def test_url_schema_headers2(self):
    #     url = "/nodes/"
    #     u, s, h = self.unis._url_schema_headers(url)
    #     self.assertEqual(u, "/nodes")
    #     self.assertEqual(s, settings.SCHEMAS["nodes"])

    # def test_url_schema_headers3(self):
    #     url = "/nodes/dea239804dbeef"
    #     u, s, h = self.unis._url_schema_headers(url)
    #     self.assertEqual(u, "/nodes/dea239804dbeef")
    #     self.assertEqual(s, settings.SCHEMAS["nodes"])

    # def test_url_schema_headers4(self):
    #     url = "/nodes?hostname=blarg"
    #     u, s, h = self.unis._url_schema_headers(url)
    #     self.assertEqual(u, "/nodes?hostname=blarg")
    #     self.assertEqual(s, settings.SCHEMAS["nodes"])

