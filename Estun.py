from multiprocessing import Process, Manager, Lock
import minimalmodbus
import serial
import configparser
from TactWatchdog import TactWatchdog
from PRONET_constants import PRONET_constants

class Estun(PRONET_constants):
    def __init__(self, shared, lock,
                    comport = "COM1",
                    slaveadress = 1,
                    protocol = ascii,
                    close_port_after_each_call = False,
                    debug = False,
                    baud = 4800,
                    stopbits = 2,
                    parity = "N",
                    bytesize = 7,
                    *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RTU = minimalmodbus.Instrument(comport,slaveadress,protocol,close_port_after_each_call,debug)
        self.RTU.serial.baudrate = baud
        self.RTU.serial.bytesize = bytesize 
        self.RTU.serial.stopbits = stopbits
        self.RTU.serial.parity = parity
        self.RTU.serial.timeout = 1
        try:
            self.Velocity = self.ReadJOGVelocity(shared, lock)
        except:
            pass ##error
    def sendRegister(self, address, value):
        self.RTU.write_register(address,value,0,16,False)

    def ReadJOGVelocity(self, shared, lock):
        try:
            return self.RTU.read_register(305,0,3,False)
        except:
            errorlevel = 0
            lock.acquire()
            shared['Error'][errorlevel] = True
            shared['Errors'] += 'communication'
            lock.release()
    @classmethod
    def Run(cls, shared, lock):
        Servo = None
        while True:
            config = configparser.ConfigParser()
            fileFeedback = config.read('servoEstun.ini')
            if fileFeedback == []:
                lock.acquire()
                shared['configurationError']=True
                shared['Errors'] += '/n Servo configuration file not found'
                shared['Error'][0] = True
                lock.release()
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






