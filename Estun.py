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

    def sendRegister(self, address, value):
        return self.RTU.write_register(address,value,0,16,False)

    def readRegister(self, address):
        return self.RTU.read_register(address,0,3,False)

    def parameterType(self, parameter = CurrentAlarm):
        return parameter[-1]

    def valueType(self, parameter = CurrentAlarm):
        return parameter[1][0]

    def parameterMask(self, parameter = CurrentAlarm, bitonly=False):
        if parameterType(parameter) == 'bit' or parameterType(parameter) == 'bin' or bitonly:
            if parameter[1][1] == 0:
                return 0b1110
            if parameter[1][1] == 1:
                return 0b1101
            if parameter[1][1] == 2:
                return 0b1011
            if parameter[1][1] == 3:
                return 0b0111
        elif parameterType(parameter) == "hex":
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
    
    def parameterAddress(self, parameter = CurrentAlarm):
        return parameter[0]

    def invertedReducedMask(self, parameter):
        mask = not parameterMask(parameter)
        if parameterType(parameter) == 'hex':
            mask /= 0xF
        return mask

    def readParameter(self, parameter):
        if parameterType == WRITE_ONLY:
            return False
        else:
            Value = readRegister(parameterAddress)
            if not valueType=='int':
                Value *= invertedReducedMask(parameter)
            return Value

    def setParameter(self, parameter = CurrentAlarm, value = 0):
        if parameterType == READ_ONLY:
            return False
        else:
            if not valueType=='int':
                currentValue = readRegister(parameterAddress)
                currentValue &= parameterMask(parameter)
                writeValue = currentValue + (value * invertedReducedMask(parameter))
            sendRegister(parameterAddress,writeValue)

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






