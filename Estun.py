import minimalmodbus
import serial
from numpy import *

class Estun():
    RTU = none
    comport = "COM1"
    baud = 4800
    stopbits = 2
    bytesize = 7
    timeout = 1
    parity = 'N'
    protocol = 'ascii'
    slaveadress = 1
    closeAfterEachCall = False
    debug = False

    def ReadJOGVelocity():
        return read_register(305,0,3,False)

    def __init__(self, *args, **kwargs):
        RTU = minimalmodbus.Instrument(comport,slaveadress,protocol,close_port_after_each_call,debug)
        RTU1.serial.baudrate = baud
        RTU1.serial.bytesize = bytesize
        RTU1.serial.stopbits = stopbits
        RTU1.serial.parity = parity
        RTU1.serial.timeout = 1
        try:
            self.ReadJOGVelocity()
        except:
            return 0







