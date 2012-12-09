import blipp.http
import unittest2
from blipp import unis_client
import socket
import time
import consts
from pprint import pprint


class UNISInstanceTests(unittest2.TestCase):
    def setUp(self):
        self.unis = unis_client.UNISInstance(
            {"unis_url":"http://dev.incntre.iu.edu/"})
        self.hn = socket.gethostname() + "UNISTEST"
        self.datetime = time.asctime()
        self.urn = "urn:ogf:network:domain=UNISTEST:node="+self.hn

    def test_everything(self):
        # register node
        r = self.unis.post("/nodes", data={"name":self.hn,
                                           "urn":self.urn,
                                           "description":"test desc",
                                           "location":{"institution":"test inst"}})
        self.assertTrue(isinstance(r, dict))
        self.node_id = r['id']
        self.nodeRef = r['selfRef']

        r2 = self.unis.get("/nodes/" + self.node_id)
        self.assertTrue(isinstance(r2, dict))

        r3 = self.unis.delete("/nodes/" + self.node_id)
        self.assertTrue(r3 == 200)

        try:
            self.unis.get("/nodes/" + self.node_id)
        except blipp.http.Blipp_HTTP_Error as e:
            self.assertTrue(e.code == 410)

        content = {"name": self.hn,
                   "urn": self.urn,
                   "desc": "unis test at " + self.datetime,
                   "location": {}}
        r4 = self.unis.post("/nodes", data=content)
        self.assertTrue(isinstance(r4, dict))
        self.node_id = r4['id']
        self.nodeRef = r4['selfRef']

        r5 = self.unis.post('/services', data=consts.SAMPLE_CONFIG)

        pprint(r5)
        self.assertTrue(isinstance(r5, dict))
        self.service_id = r5['id']

        rserv_delete = self.unis.delete("/services/" + self.service_id)
        self.assertTrue(rserv_delete == 200)

        rlast = self.unis.delete("/nodes/" + self.node_id)
        self.assertTrue(rlast == 200)

    def test_everything_AA(self):
        # /
        pass




if __name__ == '__main__':
    unittest2.main()
