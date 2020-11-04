from multiprocessing import Process, Manager, Lock
import minimalmodbus
import serial
from numpy import *
import configparser
from TactWatchdog import TactWatchdog

class Estun():
    RTU = minimalmodbus.Instrument()
    Errors = {
        'communication':False,

    }
    Velocity = 0
    def sendRegister(self, address, value):
        self.RTU.write_register(address,value,0,16,False)

    def ReadJOGVelocity(self):
        try:
            return self.RTU.read_register(305,0,3,False)
        except:
            Estun.Errors['communication']=True

# Predefiniowane argumenty powinny zawsze występować później niż zwykłe argumenty, dlatego przesunąłem shared, lock tak aby były pierwszymi argumentami
    def __init__(self, shared, lock, comport = "COM1", slaveadress = 1, protocol = ascii, close_port_after_each_call = False, debug = False, baud = 4800, stopbits = 2, parity = "N", bytesize = 7, *args, **kwargs):
        self.RTU = minimalmodbus.Instrument(comport,slaveadress,protocol,close_port_after_each_call,debug)
        self.RTU.serial.baudrate = baud
        self.RTU.serial.bytesize = bytesize 
        self.RTU.serial.stopbits = stopbits
        self.RTU.serial.parity = parity
        self.RTU.serial.timeout = 1
        try:
            self.Velocity = self.ReadJOGVelocity()
        except:
            return 0

    @classmethod
    def Run(cls, shared, lock):
        Servo = None
        while True:
            config = configparser.ConfigParser()
            fileFeedback = config.read('servoEstun.ini')
            if fileFeedback == []:
                shared['configurationError']=True
                shared['Errors'] += '/n Servo configuration file not found'
                shared['Error'][0] = True
                break
            lock.acquire()
            Alive = shared['servoModule']
            lock.release()
            if Alive:
                if Servo is None:
                    with config['COMSETTINGS'] as COMSETTINGS:
                        Servo = cls(shared, lock,
                            comport = COMSETTINGS['comport'],
                            slaveadress = COMSETTINGS['adress'],
                            protocol = COMSETTINGS['protocol'],
                            close_port_after_each_call = COMSETTINGS['close_port_after_each_call'] == 'True',
                            debug = COMSETTINGS['debug'] == 'True',
                            baud = COMSETTINGS.getboolean('baudrate'),
                            stopbits = COMSETTINGS.getboolean('stopbits'),
                            parity = COMSETTINGS['parity'],
                            bytesize = COMSETTINGS.getboolean('bytesize'))
                else:
                    lock.acquire()
                    firstAccess = shared['servoModuleFirstAccess']
                    lock.release()
                    if firstAccess == True:
                        with config['SERVOPARAMETERS'] as SERVOPARAMETERS:
                            for param in SERVOPARAMETERS:
                                Servo.sendRegister(adress=int(param),value=int(SERVOPARAMETERS[param]))
                            lock.acquire()
                            shared['servoModuleFirstAccess'] = False
                            lock.release()
                    else:
                        pass

            else:
                break






