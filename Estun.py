from multiprocessing import Process, Manager, Lock
import minimalmodbus
import serial
import configparser
import sys
import time
from TactWatchdog import TactWatchdog
from pronet_constants import Pronet_constants
from modbus_constants import Modbus_constants

class Estun(Pronet_constants, Modbus_constants, minimalmodbus.ModbusException):
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
        super().__init__(self)
        #Pronet_constants.__init__(self)
        self.RTU = minimalmodbus.Instrument(comport,slaveadress,protocol,close_port_after_each_call,debug)
        self.RTU.serial.baudrate = baud
        self.RTU.serial.bytesize = bytesize 
        self.RTU.serial.stopbits = stopbits
        self.RTU.serial.parity = parity
        self.RTU.serial.timeout = 1
        self.Lock = lock
        self.Shared = shared

    def sendRegister(self, address, value):
        try:
            return self.RTU.write_register(address,value,0,self.WRITE_REGISTER,False)
        except:
            self.Lock.acquire()
            self.Shared['Errors'] += sys.exc_info()[0]
            self.Lock.release()
            return None


    def readRegister(self, address):
        return self.RTU.read_register(address,0,self.READ_HOLDING_REGISTERS,False)

    def parameterType(self, parameter = (None,(None,None),None)):
        return parameter[2]

    def valueType(self, parameter = (None,(None,None),None)):
        return parameter[1][0]

    def parameterMask(self, parameter = (None,(None,None),None), bitonly=False):
        pType = self.valueType(parameter)
        if pType == 'bit' or pType == 'bin' or bitonly:
            if parameter[1][1] == 0:
                return 0b1110
            if parameter[1][1] == 1:
                return 0b1101
            if parameter[1][1] == 2:
                return 0b1011
            if parameter[1][1] == 3:
                return 0b0111
        elif pType == "hex":
            if parameter[1][1] == 0:
                return 0xFFF0
            if parameter[1][1] == 1:
                return 0xFF0F
            if parameter[1][1] == 2:
                return 0xF0FF
            if parameter[1][1] == 3:
                return 0x0FFF 
        else:
            return 0
    
    def parameterAddress(self, parameter = (None,(None,None),None)):
        return parameter[0]

    def invertedReducedMask(self, parameter):
        pType = self.valueType(parameter)
        pMask = self.parameterMask(parameter)
        mask = not pMask
        if pType == 'hex':
            mask /= 0xF
        return mask

    def readParameter(self, parameter):
        if self.parameterType == self.WRITE_ONLY:
            return None
        else:
            Value = self.readRegister(self.parameterAddress)
            if not self.valueType=='int':
                Value *= self.invertedReducedMask(parameter)
            return Value

    def setParameter(self, parameter = (None,(None,None),None), value = 0):
        if self.parameterType == self.READ_ONLY:
            return False
        else:
            if not self.parameterType=='int':
                currentValue = self.readRegister(self.parameterAddress)
                currentValue &= self.parameterMask(parameter)
                writeValue = currentValue + (value * self.invertedReducedMask(parameter))
            self.sendRegister(self.parameterAddress,writeValue)

class MyEstun():

    def __init__(self, shared, lock):
        super().__init__(self, shared, lock)
        self.Servo = None
        self.config = configparser.ConfigParser()
        self.servobak = configparser.ConfigParser()
        self.Shared = shared
        self.Lock = lock

    def ServoIsNone(self, config):
        with config['COMSETTINGS'] as COMSETTINGS:
            self.Servo = Estun(self.Shared, self.Lock,
                        comport = COMSETTINGS['comport'],
                        slaveadress = COMSETTINGS['adress'],
                        protocol = COMSETTINGS['protocol'],
                        close_port_after_each_call = COMSETTINGS['close_port_after_each_call'] == 'True',
                        debug = COMSETTINGS['debug'] == 'True',
                        baud = COMSETTINGS.getboolean('baudrate'),
                        stopbits = COMSETTINGS.getboolean('stopbits'),
                        parity = COMSETTINGS['parity'],
                        bytesize = COMSETTINGS.getboolean('bytesize'))

    def ServoFirstAccess(self, Servo, servobak):
        bakparams = {'SERVOPARAMS':{}}
        for n in range(1000):
            data = Servo.read_register(n)
            if data is not None:
                bakparams['SERVOPARAMS'][str(n)] = data
                self.servobak.write('servobak'+ time.time() +'.ini')
                    #    with config['SERVOPARAMETERS'] as SERVOPARAMETERS:
                    #        for n, param in enumerate(SERVOPARAMETERS):
                    #            Servo.sendRegister(adress=int(param),value=int(SERVOPARAMETERS[param]))
                    #        lock.acquire()
                    #        shared['servoModuleFirstAccess'] = False
                    #        lock.release()

    def ServoLoop(self):
        pass

    @classmethod
    def Run(cls, shared, lock):
        control = cls(shared, lock)
        while True:   
            fileFeedback = control.config.read('servoEstun.ini')
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
                if control.Servo is None:
                    control.ServoIsNone(fileFeedback)
                else:
                    lock.acquire(control.config)
                    firstAccess = shared['servoModuleFirstAccess']
                    lock.release()
                    if firstAccess == True:
                        control.ServoFirstAccess(control.Servo,control.servobak)
                    else:
                        control.ServoLoop()
            else:
                break






