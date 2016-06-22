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
'''
Usage:
blippcmd [<ipc_file>]
'''
from docopt import docopt
import cmd
import zmq
from blipp.config_server_api import POLL_CONFIG, RELOAD
from blipp.unis_client import UNISInstance
import json
import shlex
import pprint

context = zmq.Context()
socket = context.socket(zmq.REQ)

class BlippCmd(cmd.Cmd):
    def __init__(self):
        self.prompt = col.PROMPT + "blipp>>> " + col.ENDC
        self.config = {}
        self.cwc = self.config
        self.unis = None
        self.cwd_list = []
        cmd.Cmd.__init__(self)

    def do_cd(self, path):
        '''Change the current level of view of the config to be at <key>
        cd <key>'''
        if path=="" or path[0]=="/":
            new_wd_list = path[1:].split("/")
        else:
            new_wd_list = self.cwd_list + path.split("/")
        try:
            cwc, new_wd_list = self._conf_for_list(new_wd_list)
        except ConfigurationError as e:
            print col.FAIL + str(e) + col.ENDC
            return
        self.cwd_list = new_wd_list
        self.cwc = cwc

    def complete_cd(self, text, l, b, e):
        return [ x for x,y in self.cwc.iteritems()
                 if isinstance(y, dict) and x.startswith(text) ]

    def do_ls(self, key):
        '''Show the top level of the current working config, or top level of config under [key]
        ls [key]'''
        conf = self.cwc
        if key:
            try:
                conf = conf[key]
            except KeyError:
                print "No such key %s" % key
                return
        for k,v in conf.iteritems():
            if isinstance(v, dict):
                print col.DIR + k + col.ENDC
            else:
                print "%s: %s" % (k, v)

    def complete_ls(self, text, l, b, e):
        return [ x for x,y in self.cwc.iteritems()
                 if isinstance(y, dict) and x.startswith(text) ]

    def do_lsd(self, key):
        '''Show all config from current level down... or all config under [key]
        lsd [key]'''
        conf = self.cwc
        if key:
            try:
                conf = conf[key]
            except KeyError:
                print "No such key %s" % key
        pprint.pprint(conf)

    def complete_lsd(self, text, l, b, e):
        return [ x for x,y in self.cwc.iteritems()
                 if isinstance(y, dict) and x.startswith(text) ]

    def do_pwd(self, key):
        '''Show current path in config separated by slashes
        pwd'''
        print "/" + "/".join(self.cwd_list)

    def do_show(self, none):
        '''Get config from blipp if there are no changes since last get
        show'''
        socket.send(POLL_CONFIG)
        msg = socket.recv()
        if not msg:
            print pprint.pformat(self.config)
        else:
            self.config = json.loads(msg)
            self._set_cwc()
            print pprint.pformat(self.config)
            self.unis = UNISInstance(self.config)

    def do_set(self, line):
        '''Set a key in local config
        set <key> <value>'''
        line = shlex.split(line)
        if len(line)<2:
            print "Usage: set <key> <value>"
            return
        val = self._val_from_input(line[1])
        self.cwc[line[0]] = val

    def complete_set(self, text, l, b, e):
        if b==4:
            return [ x for x,y in self.cwc.iteritems()
                     if x.startswith(text) ]
        else:
            return []

    def do_del(self, key):
        '''Delete a key from the configuration at this level
        del <key>'''
        try:
            del self.cwc[key]
        except KeyError:
            print col.FAIL + "Error: Key %s not found" % key + col.ENDC

    def complete_del(self, text, l, b, e):
        return [ x for x in self.cwc.keys()
                 if x.startswith(text) ]

    def do_reload(self, none):
        '''push current config to unis and force blipp to call reload_all()
        and refresh its running state with config in unis
        reload'''
        self.do_put("")
        socket.send(RELOAD)
        msg = socket.recv()
        print msg

    def do_put(self, none):
        '''Push current configuration to unis
        put'''
        if not self.unis:
            print col.FAIL + "ERROR: no unis?" + col.ENDC
            return
        self.unis.put("/services/" + self.config["id"], self.config)

    def do_mkdir(self, name):
        '''Create an empty config dict with key <name> at the current
        level
        mkdir <name>
        '''
        self.cwc[name] = {}

    def do_EOF(self, line):
        return True

    def _val_from_input(self, inp):
        '''Take user input, and try to convert it to JSON appropriate
        python values.
        '''
        val = inp
        try:
            val = int(inp)
            return val
        except Exception:
            val = inp
        if val == "false":
            return False
        if val == "true":
            return True
        if (val[0] == "'" and val[-1] == "'") or\
                (val[0] == '"' and val[-1] == '"'):
            return val[1:-1]
        return val

    def _set_cwc(self):
        '''Set the current working configuration to what it should be
        based on the cwd_list. If the path doesn't exist, set cwc to
        the top level and clear the cwd_list.
        '''
        try:
            self.cwc, self.cwd_list = self._conf_for_list()
        except ConfigurationError:
            self.cwc = self.config
            self.cwd_list = []

    def _conf_for_list(self, cwd_list=None):
        '''Takes in a list representing a path through the config
        returns a tuple containing the current working config, and the
        "collapsed" final path (meaning it has no .. entries.
        '''
        if not cwd_list:
            cwd_list = self.cwd_list
        cwc_stack = []
        cwc = self.config
        num = 0
        for kdir in cwd_list:
            if kdir == "":
                continue
            num += 1
            if kdir == ".." and cwc_stack:
                cwc = cwc_stack.pop()[0]
                continue
            elif kdir == "..":
                continue
            try:
                ocwc = cwc
                cwc = cwc[kdir]
                cwc_stack.append((ocwc, kdir))
            except KeyError:
                raise ConfigurationError(num, kdir, cwd_list)
        return (cwc, [ x[1] for x in cwc_stack ])


class ConfigurationError(Exception):
    def __init__(self, num, key, dir_list):
        self.num = num
        self.key = key
        self.dir = "/" + "/".join(dir_list)

    def __str__(self):
        return "No such path through config at pos:%d %s in %s"%(self.num, self.key, self.dir)

class col:
    HEADER = '\033[35m'# PINK
    DIR = '\033[34m' # BLUE
    PROMPT = '\033[32m' # GREEN
    WARNING = '\033[33m' # YELLOW
    FAIL = '\033[31m' # RED
    ENDC = '\033[39m' # BLACK

def main():
    ipc_file = "/tmp/blipp_socket_zcWcfO0ydo"
    socket.connect("ipc://" + ipc_file)
    BlippCmd().cmdloop()

if __name__ == '__main__':
    arguments = docopt(__doc__, version='blippcmd 0.1')
    if arguments["<ipc_file>"]:
        ipc_file = arguments["<ipc_file>"]
    else:
        ipc_file = "/tmp/blipp_socket_zcWcfO0ydo"
    socket.connect("ipc://" + ipc_file)
    BlippCmd().cmdloop()
