#
# Server for blipp configuration
# and control
#
#
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
            if self.socket.poll(finish_time - cur_time):
                message = self.socket.recv()
                ret = self._handle_message(message)
                self.socket.send(ret)
                if RELOAD in message:
                    break
            cur_time = time.time()
        return False

    def _handle_message(self, message):
        com, s, args = message.partition(' ')
        args, kwargs = self._parse_args(args.split())
        if POLL_CONFIG in com or GET_CONFIG in com:
            if self.changed:
                return json.dumps(self.conf_obj.config)
        elif RELOAD in com:
            return "reloading"

        # try:
        #     attr = getattr(self.conf_obj, com)
        # except AttributeError:
        #     return "Error: No attribute '%s' in configuration object" % com
        # if hasattr(attr, "__call__"):
        #     try:
        #         return pprint.pformat(attr(*args, **kwargs))
        #     except Exception as e:
        #         logger.exc('_handle_message', e)
        #         return "Exception %s, message '%s'" % (e.__class__, e.message)
        # else:
        #     return pprint.pformat(attr)

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
