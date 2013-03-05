import cmd
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("ipc:///tmp/blipp")

class BlippCmd(cmd.Cmd):
    def __init__(self):
        self.prompt = "blipp: "
        cmd.Cmd.__init__(self)

    def default(self, line):
        socket.send(line)
        msg = socket.recv()
        print msg

    def do_get(self, key):
        socket.send("__getitem__ " + key)
        msg = socket.recv()
        print msg

    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    BlippCmd().cmdloop()
