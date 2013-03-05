#
# Server for blipp configuration
# and control
#
#
import zmq
import pprint
import settings

logger = settings.get_logger('config_server')

class ConfigServer:
    def __init__(self, conf_obj):
        self.context = zmq.Context()
        self.conf_obj = conf_obj
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("ipc:///tmp/blipp")

    def listen(self, timeout):
        if self.socket.poll(timeout):
            message = self.socket.recv()
            ret = self._handle_message(message)
            self.socket.send(ret)

    def _handle_message(self, message):
        com, s, args = message.partition(' ')
        args, kwargs = self._parse_args(args.split())
        try:
            attr = getattr(self.conf_obj, com)
        except AttributeError:
            return "Error: No attribute '%s' in configuration object" % com
        if hasattr(attr, "__call__"):
            try:
                return pprint.pformat(attr(*args, **kwargs))
            except Exception as e:
                logger.exc('_handle_message', e)
                return "Exception %s, message '%s'" % (e.__class__, e.message)
        else:
            return pprint.pformat(attr)

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
