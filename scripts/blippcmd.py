import cmd
import zmq
from blipp.config_server_api import POLL_CONFIG, GET_CONFIG, RELOAD
from blipp.unis_client import UNISInstance
import json
import pprint

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("ipc:///tmp/blipp")

class BlippCmd(cmd.Cmd):
    def __init__(self):
        self.prompt = "blipp: "
        self.config = {}
        self.unis = None
        cmd.Cmd.__init__(self)

    def default(self, line):
        '''Just send whatever you type straight to the config_server'''
        socket.send(line)
        msg = socket.recv()
        print msg

    def do_getrunning(self, line):
        '''Get config from blipp whether cached or not'''
        socket.send(GET_CONFIG)
        msg = socket.recv()
        print msg

    def do_show(self, none):
        '''Get config from blipp if there are no changes since last get'''
        socket.send(POLL_CONFIG)
        msg = socket.recv()
        if not msg:
            print pprint.pformat(self.config)
        else:
            self.config = json.loads(msg)
            print pprint.pformat(self.config)
            self.unis = UNISInstance(self.config)

    def do_set(self, line):
        '''set a key in local config'''
        line = line.split()
        val = self._val_from_input(line[1])
        self.config[line[0]] = val

    def do_reload(self, none):
        '''force blipp to call reload_all() and refresh its running state with config in unis'''
        socket.send(RELOAD)
        msg = socket.recv()
        print msg

    def do_put(self, none):
        if not self.unis:
            print "ERROR: no unis?"
            return
        self.unis.put("/services/" + self.config["id"], self.config)

    def do_EOF(self, line):
        return True

    def _val_from_input(self, input):
        val = input
        try:
            val = int(input)
            return val
        except Exception:
            val = input
        if val == "false":
            return False
        if val == "true":
            return True
        if (val[0] == "'" and val[-1] == "'") or\
                (val[0] == '"' and val[-1] == '"'):
            return val[1:-1]
        return val

if __name__ == '__main__':
    BlippCmd().cmdloop()
