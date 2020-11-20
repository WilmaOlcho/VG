import minimalmodbus
import socket

class Robot():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

class Kawasaki(Robot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.hostname = ''
        self.port = 10000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class RobotIO(Kawasaki):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)