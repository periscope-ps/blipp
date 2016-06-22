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
Server for blipp configuration and control via cmd line interface.
'''
import zmq
import settings
import json
import time
from config_server_api import RELOAD, GET_CONFIG, POLL_CONFIG


logger = settings.get_logger('config_server')

class ConfigServer:
    def __init__(self, conf_obj):
        self.context = zmq.Context()
        self.conf_obj = conf_obj
        self.changed = True
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("ipc:///tmp/blipp_socket_zcWcfO0ydo")

    def listen(self, timeout):
        cur_time = time.time()
        finish_time = cur_time + timeout
        while cur_time < finish_time:
            logger.info("listen", msg="polling for %d"%(finish_time-cur_time))
            if self.socket.poll((finish_time - cur_time)*1000):
                message = self.socket.recv()
                ret = self._handle_message(message)
                self.socket.send(ret)
                if RELOAD in message:
                    return True
            cur_time = time.time()
        return True

    def _handle_message(self, message):
        com, s, args = message.partition(' ')
        args, kwargs = self._parse_args(args.split())
        if POLL_CONFIG in com or GET_CONFIG in com:
            if self.changed:
                return json.dumps(self.conf_obj.config)
        elif RELOAD in com:
            return "reloading"

    def _parse_args(self, args):
        ret_args = []
        kwargs = {}
        for arg in args:
            k, e, v = arg.partition('=')
            if not e:
                ret_args.append(arg)
            else:
                kwargs[k] = v
        return ret_args, kwargs
