import minimalmodbus
import serial
import configparser
import sys
from functools import lru_cache
from TactWatchdog import TactWatchdog as WDT
from pronet_constants import Pronet_constants
from modbus_constants import Modbus_constants
from misc import BlankFunc, writeInLambda, dictKeyByVal
from StaticLock import SharedLocker

class Estun(Pronet_constants, Modbus_constants, minimalmodbus.ModbusException, SharedLocker):
    def __init__(self,
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

    def sendRegister(self, address, value):
        try:
            return self.RTU.write_register(address,value,0,self.WRITE_REGISTER,False)
        except:
            self.lock.acquire()
            self.shared['Errors'] += sys.exc_info()[0]
            self.lock.release()
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

class MyEstun(Estun, SharedLocker):
    def homing(self):
        if self.timerhoming == None:
            self.timerhoming = WDT.WDT(scale = 's',limitval = 30, errToRaise='Servo Homing Time exceeded', errorlevel=10)
        if self.readDOG():
            self.lock.acquire()
            self.estun['homing'] = False
            self.events['EstunHomingComplete'] = True
            self.lock.release()
            self.timerhoming.Destruct()
        else:
            self.lock.acquire()
            self.estunModbus['SHOM'] = False if self.estunModbus['TGON'] else True
            self.lock.release()
            # homing key reaction:
            #   set homing input on servo for a while, resets when servo runs
            #   looking for DOG input for 30s
            #   DOG input destructs timer and close homing procedure 

    def step(self):
        if self.timerstep == None:
            self.timerstep = WDT.WDT(scale = 's',limitval = 10, errToRaise='Servo Step Time exceeded', errorlevel=10)
            self.lock.acquire()
            self.estunModbus['PCON'] = False if self.estunModbus['TGON'] else True
            if self.estunModbus['COIN']:
                self.estun['step'] = False
                self.estun['stepComplete'] = True
                self.timerstep.Destruct()
            self.lock.release()
            #step key reaction:
            #set PCON for a while, reset whne servo runs
            #looking for 10s for coin input
            #coin input destructs wdt timer and close step procedure

    def resetAlarm(self):
        if self.readParameter(self.CurrentAlarm) != 0:
            self.setParameter(self.ClearCurrentAlarms, 0x01)
            self.lock.acquire()
            self.estun['reset'] = False
            self.events['EstunResetDone'] = True
            self.lock.release()

    def readDOG(self):
        self.lock.acquire()
        DOGv = self.estunModbus['ORG']
        self.lock.release()
        return DOGv

    @lru_cache(maxsize = 2)
    def getIOTerminals(self, anythingChanged = False):
        if anythingChanged:
            default = None
            terminals = { 
                'S-ON':default,
                'P-CON':default,
                'P-OT':default,
                'N-OT':default,
                'ALMRST':default,
                'CLR':default,
                'P-CL':default,
                'N-CL':default,
                'G-SEL':default,
                'JDPOS-JOG+':default,
                'JDPOS-JOG-':default,
                'JDPOS-HALT':default,
                'HmRef':default,
                'SHOM':default,
                'ORG':default,
                '/COIN/VMCP':default,
                '/TGON':default,
                '/S-RDY':default,
                '/CLT':default,
                '/BK':default,
                '/PGC':default,
                'OT':default,
                '/RD':default,
                '/HOME':default}
            @lru_cache(maxsize = 32)
            def getTerminal(terminal):
                term=self.dterminals[terminal]
                termv=self.dterminals[terminal +'v']
                paramdict = self.config['SERVOPARAMETERS']
                Byval = self.invertedReducedMask(term & paramdict[str(term[0])])
                return dictKeyByVal(termv, Byval)
            for val in self.dterminalTypes: terminals[getTerminal(str(val[0]))] = val
            return terminals

    def IOControl(self):
        terminals = self.getIOTerminals(True)
        buscontrol = [  self.BusCtrlInputNode1_14,self.BusCtrlInputNode1_15,
                        self.BusCtrlInputNode1_16,self.BusCtrlInputNode1_17,
                        self.BusCtrlInputNode1_39,self.BusCtrlInputNode1_40,
                        self.BusCtrlInputNode1_41,self.BusCtrlInputNode1_42]
        for n, param in enumerate(self.dterminalTypes[:8]):
            if self.config[buscontrol[n][0]] & self.invertedReducedMask(buscontrol[n]):
                self.setParameter(param,self.estunModbus[dictKeyByVal(terminals,self.dterminalTypes[n])])
            else:
                self.estunModbus[dictKeyByVal(terminals,self.dterminalTypes[n])] = self.readParameter(param)
        for n, param in enumerate(self.dterminalTypes[8:]):
             self.estunModbus[dictKeyByVal(terminals,self.dterminalTypes[n])] = self.readParameter(param)

    def __init__(self, configFile, *args, **kwargs):
        self.control_switch = {
            'procedure':{
                'homing':self.homing,
                'step':self.step,
                'reset':self.resetAlarm,
                'DOG':self.readDOG,
                'IOControl':self.IOControl}} 
        self.config = configparser.ConfigParser()
        self.servobak = configparser.ConfigParser()
        fileFeedback = self.config.read(configFile)
        if fileFeedback == []:
            self.lock.acquire()
            self.shared['configurationError']=True
            self.shared['Errors'] += '/n Servo configuration file not found'
            self.errorlevel[0] = True
            self.estun['Alive'] = True
            self.lock.release()

        self.lock.acquire()
        self.Alive = self.estun['Alive']
        self.lock.release()
        COMSETTINGS = self.config['COMSETTINGS']
        super().__init__(   comport = COMSETTINGS['comport'],
                            slaveadress = COMSETTINGS['adress'],
                            protocol = COMSETTINGS['protocol'],
                            close_port_after_each_call = COMSETTINGS['close_port_after_each_call'] == 'True',
                            debug = COMSETTINGS['debug'] == 'True',
                            baud = COMSETTINGS.getboolean('baudrate'),
                            stopbits = COMSETTINGS.getboolean('stopbits'),
                            parity = COMSETTINGS['parity'],
                            bytesize = COMSETTINGS['bytesize'], *args, **kwargs)
        while self.Alive:
            self.lock.acquire()
            firstAccess = self.estun['servoModuleFirstAccess']
            self.lock.release()
            if firstAccess:
                self.ServoFirstAccess()
            else:
                self.ServoLoop()

    def ServoLoop(self):
        with lambda instance, stringval: instance.WithLock(instance, lambda instance, stringval: instance.shared['Estun']['stringval']) as IsTrue:
            if IsTrue(self,'homing'): self.control_switch['homing'](self)
            if IsTrue(self,'step'): self.control_switch['step'](self)
            if IsTrue(self,'reset'): self.control_switch['reset'](self)
            if IsTrue(self,'DOG'): self.control_switch['DOG'](self)
            self.control_switch['DOGIOControl'](self)

    def ServoFirstAccess(self):
        bakparams = {'SERVOPARAMS':{}}
        for n in range(1000):
            data = self.read_register(n)
            if data is not None:
                bakparams['SERVOPARAMS'][str(n)] = data
        self.servobak.read_dict(bakparams)
        self.servobak.write('servobak'+ time.time() +'.ini')
        with self.config['SERVOPARAMETERS'] as SERVOPARAMETERS:
            for n, param in enumerate(SERVOPARAMETERS):
                self.sendRegister(adress=int(param),value=int(SERVOPARAMETERS[param]))
                self.lock.acquire()
                self.estun['servoModuleFirstAccess'] = False
                self.lock.release()


    