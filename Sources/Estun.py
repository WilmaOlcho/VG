import minimalmodbus
import serial
import configparser
import sys
import time
from functools import lru_cache
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources.pronet_constants import Pronet_constants
from Sources.modbus_constants import Modbus_constants
from Sources.misc import BlankFunc, writeInLambda, dictKeyByVal, ErrorEventWrite

class Estun(minimalmodbus.Instrument, Pronet_constants, Modbus_constants):
    def __init__(self, lockerinstance,
            comport = "COM1",
            slaveaddress = 1,
            protocol = ascii,
            close_port_after_each_call = False,
            debug = False,
            baud = 4800,
            stopbits = 2,
            parity = "N",
            bytesize = 7,
            *args, **kwargs):
        try:
            Pronet_constants.__init__(self)
            Modbus_constants.__init__(self)
            minimalmodbus.Instrument.__init__(self, comport,slaveaddress,mode = protocol,close_port_after_each_call=close_port_after_each_call,debug=debug,*args, **kwargs)
            self.serial.baudrate = baud
            self.serial.bytesize = bytesize 
            self.serial.stopbits = stopbits
            self.serial.parity = parity
            self.serial.timeout = 1
        except Exception as e:
            errormessage = 'Estun communication error: ' + str(e)
            ErrorEventWrite(lockerinstance, errormessage)

    def sendRegister(self, lockerinstance, address, value):
        try:
            return self.write_register(address,value,0,self.WRITE_REGISTER,False)
        except Exception as e:
            errormessage = 'Estun sendRegister Error: ' + str(e)
            ErrorEventWrite(lockerinstance, errormessage)
            return None

    def readRegister(self, lockerinstance, address):
        return self.read_register(address,0,self.READ_HOLDING_REGISTERS,False)

    def parameterType(self, lockerinstance, parameter = (None,(None,None),None)):
        return parameter[2]

    def valueType(self, lockerinstance, parameter = (None,(None,None),None)):
        return parameter[1][0]

    def parameterMask(self, lockerinstance, parameter = (None,(None,None),None), bitonly=False):
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
    
    def parameterAddress(self, lockerinstance, parameter = (None,(None,None),None)):
        return parameter[0]

    def invertedReducedMask(self, lockerinstance, parameter):
        pType = self.valueType(parameter)
        pMask = self.parameterMask(parameter)
        mask = not pMask
        if pType == 'hex':
            mask /= 0xF
        return mask

    def readParameter(self, lockerinstance, parameter):
        if self.parameterType == self.WRITE_ONLY:
            return None
        else:
            Value = self.readRegister(lockerinstance, self.parameterAddress)
            if not self.valueType=='int':
                Value *= self.invertedReducedMask(lockerinstance, parameter)
            return Value

    def setParameter(self, lockerinstance, parameter = (None,(None,None),None), value = 0):
        if self.parameterType == self.READ_ONLY:
            return False
        else:
            if not self.parameterType=='int':
                currentValue = self.readRegister(lockerinstance, self.parameterAddress)
                currentValue &= self.parameterMask(lockerinstance, parameter)
                writeValue = currentValue + (value * self.invertedReducedMask(lockerinstance, parameter))
            self.sendRegister(lockerinstance, self.parameterAddress, writeValue)

class MyEstun(Estun):
    def homing(self, lockerinstance):
        if self.timerhoming == None:
            self.timerhoming = WDT.WDT(lockerinstance, scale = 's',limitval = 30, errToRaise='Servo Homing Time exceeded', errorlevel=10)
        if self.readDOG(lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].estun['homing'] = False
            lockerinstance[0].events['EstunHomingComplete'] = True
            lockerinstance[0].lock.release()
            self.timerhoming.Destruct()
        else:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].estunModbus['SHOM'] = False if lockerinstance[0].estunModbus['TGON'] else True
            lockerinstance[0].lock.release()
            # homing key reaction:
            #   set homing input on servo for a while, resets when servo runs
            #   looking for DOG input for 30s
            #   DOG input destructs timer and close homing procedure 

    def step(self, lockerinstance):
        if self.timerstep == None:
            self.timerstep = WDT.WDT(lockerinstance, scale = 's',limitval = 10, errToRaise='Servo Step Time exceeded', errorlevel=10)
            lockerinstance[0].lock.acquire()
            lockerinstance[0].estunModbus['PCON'] = False if lockerinstance[0].estunModbus['TGON'] else True
            if lockerinstance[0].estunModbus['COIN']:
                lockerinstance[0].estun['step'] = False
                lockerinstance[0].estun['stepComplete'] = True
                self.timerstep.Destruct()
            lockerinstance[0].lock.release()
            #step key reaction:
            #set PCON for a while, reset whne servo runs
            #looking for 10s for coin input
            #coin input destructs wdt timer and close step procedure

    def resetAlarm(self, lockerinstance):
        if self.readParameter(lockerinstance, self.CurrentAlarm) != 0:
            self.setParameter(lockerinstance, self.ClearCurrentAlarms, 0x01)
            lockerinstance[0].lock.acquire()
            lockerinstance[0].estun['reset'] = False
            lockerinstance[0].events['EstunResetDone'] = True
            lockerinstance[0].lock.release()

    def readDOG(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        DOGv = lockerinstance[0].estunModbus['ORG']
        lockerinstance[0].lock.release()
        return DOGv

    @lru_cache(maxsize = 2)
    def getIOTerminals(self, lockerinstance, anythingChanged = False):
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
                Byval = self.invertedReducedMask(lockerinstance, term & paramdict[str(term[0])])
                return dictKeyByVal(termv, Byval)
            for val in self.dterminalTypes: terminals[getTerminal(str(val[0]))] = val
            return terminals

    def IOControl(self, lockerinstance):
        terminals = self.getIOTerminals(True)
        buscontrol = [  self.BusCtrlInputNode1_14,self.BusCtrlInputNode1_15,
                        self.BusCtrlInputNode1_16,self.BusCtrlInputNode1_17,
                        self.BusCtrlInputNode1_39,self.BusCtrlInputNode1_40,
                        self.BusCtrlInputNode1_41,self.BusCtrlInputNode1_42]
        for n, param in enumerate(self.dterminalTypes[:8]):
            if (int(self.config['SERVOPARAMETERS'][str(buscontrol[n][0])]) & int(self.invertedReducedMask(lockerinstance, buscontrol[n]))):
                self.setParameter(param,lockerinstance[0].estunModbus[dictKeyByVal(terminals,self.dterminalTypes[n])])
            else:
                lockerinstance[0].estunModbus[dictKeyByVal(terminals,self.dterminalTypes[n])] = self.readParameter(lockerinstance, param)
        for n, param in enumerate(self.dterminalTypes[8:]):
             lockerinstance[0].estunModbus[dictKeyByVal(terminals,self.dterminalTypes[n])] = self.readParameter(lockerinstance, param)

    def __init__(self, lockerinstance, configFile, *args, **kwargs):
        self.control_switch = {
            'procedure':{
                'homing':self.homing,
                'step':self.step,
                'reset':self.resetAlarm,
                'DOG':self.readDOG,
                'IOControl':self.IOControl}} 
        self.timerhoming = None
        self.timerstep = None
        self.config = configparser.ConfigParser()
        self.servobak = configparser.ConfigParser()
        fileFeedback = self.config.read(configFile)
        if not fileFeedback:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].shared['configurationError']=True
            lockerinstance[0].shared['Errors'] += '\n Servo configuration file not found'
            lockerinstance[0].errorlevel[0] = True
            lockerinstance[0].lock.release()
        else:
            COMSETTINGS = self.config['COMSETTINGS']
            while True:
                try:
                    skwargs = { 'comport':COMSETTINGS['comport'],
                                'slaveaddress':COMSETTINGS.getint('adress'),
                                'protocol':COMSETTINGS['protocol'],
                                'close_port_after_each_call':COMSETTINGS.getboolean('close_port_after_each_call') == 'True',
                                'debug':COMSETTINGS.getboolean('debug') == 'True',
                                'baud':COMSETTINGS.getint('baudrate'),
                                'stopbits':COMSETTINGS.getint('stopbits'),
                                'parity':COMSETTINGS.get('parity'),
                                'bytesize':COMSETTINGS.getint('bytesize')}
                    super().__init__(   lockerinstance, **skwargs, **kwargs)
                    if self.serial is None: raise Exception('Serial is not open: ' + str(skwargs.items()))
                except Exception as e:
                    errmessage = 'Estun init error:' + str(e)
                    ErrorEventWrite(lockerinstance, errmessage)
                else:
                    lockerinstance[0].lock.acquire()
                    firstAccess = lockerinstance[0].estun['servoModuleFirstAccess']
                    lockerinstance[0].estun['Alive'] = True
                    self.Alive = True
                    lockerinstance[0].lock.release()
                    if firstAccess: self.ServoFirstAccess(lockerinstance)
                    self.ServoLoop(lockerinstance)
                    break
                finally:
                    lockerinstance[0].lock.acquire()
                    letdie = lockerinstance[0].events['closeApplication']
                    lockerinstance[0].lock.release()
                    if letdie: break

    def ServoLoop(self, lockerinstance):
        while self.Alive:
            lockerinstance[0].lock.acquire()
            homing, step, reset, Dog = lockerinstance[0].estun['homing'], lockerinstance[0].estun['step'], lockerinstance[0].estun['reset'], lockerinstance[0].estun['DOG']
            lockerinstance[0].lock.release()
            try:
                if homing: self.control_switch['homing'](lockerinstance)
            except Exception as e:
                errmessage = 'Estun homing error:' + str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            try:
                if step: self.control_switch['step'](lockerinstance)
            except Exception as e:
                errmessage = 'Estun step error:' + str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            try:
                if reset: self.control_switch['reset'](lockerinstance)
            except Exception as e:
                errmessage = 'Estun reset error:' + str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            try:
                if Dog: self.control_switch['DOG'](lockerinstance)
            except Exception as e:
                errmessage = 'Estun DOG error:' + str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            try:
                self.IOControl(lockerinstance)
            except Exception as e:
                errmessage = 'Estun IOControl error:' + str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)

    def ServoFirstAccess(self, lockerinstance):
        bakparams = {'SERVOPARAMS':{}}
        for n in range(875):
            try:
                data = self.readRegister(lockerinstance, n)
            except Exception as e:
                errstring = "ServoFirstAccessError " + str(e) + ' Address: {}'.format(n)
                ErrorEventWrite(lockerinstance, errstring, errorlevel = 10)
            else:
                if data is not None: bakparams['SERVOPARAMS'][str(n)] = data
                #print('{} {}'.format(n,data))
        self.servobak.read_dict(bakparams)
        self.servobak.write(open('servobak'+ str(time.time()) +'.ini','w'))
        #SERVOPARAMETERS = self.config['SERVOPARAMETERS']
        #for n, param in enumerate(SERVOPARAMETERS):
        #    self.sendRegister(lockerinstance, address=int(param),value=int(SERVOPARAMETERS[param]))
        lockerinstance[0].lock.acquire()
        lockerinstance[0].estun['servoModuleFirstAccess'] = False
        lockerinstance[0].lock.release()


    