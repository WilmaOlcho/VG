from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.transaction import ModbusAsciiFramer
import serial
import configparser
import sys
import time
from functools import lru_cache
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources.pronet_constants import Pronet_constants
from Sources.modbus_constants import Modbus_constants
from Sources.misc import BlankFunc, writeInLambda, dictKeyByVal, ErrorEventWrite

class Estun(ModbusSerialClient, Pronet_constants, Modbus_constants):
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
            ModbusSerialClient.__init__(self,bytesize = bytesize, baudrate = baud, parity = parity, port = comport,timeout = 2, stopbits = stopbits, method = protocol)
        except Exception as e:
            errormessage = 'Estun communication error: ' + str(e)
            ErrorEventWrite(lockerinstance, errormessage)

    def sendRegister(self, lockerinstance, address, value):
        try:
            self.connect()
            self.write_register(address, value, unit=0x1)
            self.close()
            return True
        except Exception as e:
            errormessage = 'Estun sendRegister Error: ' + str(e)
            ErrorEventWrite(lockerinstance, errormessage)
            return None

    def readRegister(self, lockerinstance, address):
        while True:
            try:
                self.connect()
                result = self.read_holding_registers(address,1,unit = 0x1)
                self.close()
                break
            except:
                pass
        return result.registers[0]

    def parameterType(self, lockerinstance, parameter = (None,(None,None),None)):
        if len(parameter) < 3 and len(parameter) > 1:
            if isinstance(parameter[1],str):
                pass
        return parameter[2]

    def valueType(self, lockerinstance, parameter = (None,(None,None),None)):
        return parameter[1][0]

    def parameterMask(self, lockerinstance, parameter = (None,(None,None),None), bitonly=False):
        pType = self.valueType(lockerinstance, parameter)
        if pType == 'bit' or pType == 'bin' or bitonly:
            if parameter[1][1] == 0:
                return 0b1110
            if parameter[1][1] == 1:
                return 0b1101
            if parameter[1][1] == 2:
                return 0b1011
            if parameter[1][1] == 3:
                return 0b0111
        elif pType == 'hex':
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
        #pType = self.valueType(lockerinstance, parameter)
        pMask = self.parameterMask(lockerinstance, parameter)
        mask = ~pMask & 0xFFFF
        #if pType == 'hex':
        #    mask //= 0xF
        
        return mask

    def readParameter(self, lockerinstance, parameter):
        if self.parameterType(lockerinstance, parameter) == self.WRITE_ONLY:
            return None
        else:
            Value = self.readRegister(lockerinstance, self.parameterAddress(lockerinstance, parameter))
            if not self.valueType(lockerinstance, parameter)=='int':
                Value *= self.invertedReducedMask(lockerinstance, parameter)
            return Value

    def setParameter(self, lockerinstance, parameter = (None,(None,None),None), value = 0):
        if self.parameterType(lockerinstance, parameter) == self.READ_ONLY:
            return False
        else:
            writeValue = value
            #if not self.parameterType(lockerinstance, parameter)=='int':
            #    currentValue = self.readRegister(lockerinstance, self.parameterAddress(lockerinstance, parameter))
            #    currentValue &= self.parameterMask(lockerinstance, parameter)
            #    writeValue = currentValue + (value * self.invertedReducedMask(lockerinstance, parameter))
            self.sendRegister(lockerinstance, self.parameterAddress(lockerinstance, parameter), writeValue)

class MyEstun(Estun):
    def homing(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        WDTActive = 'WDTServo Homing Time exceeded' in lockerinstance[0].wdt
        lockerinstance[0].estunModbus['N-CL'] = True
        lockerinstance[0].lock.release()
        if not WDTActive:
            WDT.WDT(lockerinstance, scale = 's',limitval = 60, eventToCatch='EstunHomingComplete', errToRaise='Servo Homing Time exceeded', errorlevel=10)
        if self.readDOG(lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].events['EstunHomingComplete'] = True
            lockerinstance[0].estunModbus['N-CL'] = False
            lockerinstance[0].estun['homing'] = False
            lockerinstance[0].lock.release()
            # homing key reaction:
            #   set homing input on servo for a while, resets when servo runs
            #   looking for DOG input for 30s
            #   DOG input destructs timer and close homing procedure 

    def step(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        WDTActive = 'WDTServo Step Time exceeded' in lockerinstance[0].wdt
        lockerinstance[0].lock.release()
        self.IOControl(lockerinstance)
        lockerinstance[0].lock.acquire()
        lockerinstance[0].estunModbus['P-CON'] = True
        srdy = lockerinstance[0].estunModbus['/S-RDY']
        lockerinstance[0].lock.release()
        if srdy and WDTActive:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].estun['stepComplete'] = True
            lockerinstance[0].estunModbus['P-CON'] = False
            lockerinstance[0].estun['step'] = False
            lockerinstance[0].lock.release()
        elif srdy and not WDTActive:
            WDT.WDT(lockerinstance, scale = 's',limitval = 15, eventToCatch='stepComplete', errToRaise='Servo Step Time exceeded', errorlevel=10)
        else:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].estunModbus['P-CON'] = False
            lockerinstance[0].estun['step'] = False
            lockerinstance[0].lock.release()
            #step key reaction:
            #set PCON for a while, reset whne servo runs
            #looking for 10s for coin input
            #coin input destructs wdt timer and close step procedure

    def resetAlarm(self, lockerinstance):
        if self.readParameter(lockerinstance, self.CurrentAlarm) != 0:
            self.setParameter(lockerinstance, self.ClearCurrentAlarms, 0x01)
            lockerinstance[0].lock.acquire()
            lockerinstance[0].events['EstunResetDone'] = True
            lockerinstance[0].estun['reset'] = False
            lockerinstance[0].lock.release()
        else:
            self.setParameter(lockerinstance, self.InputSignalState)
            lockerinstance[0].lock.acquire()
            lockerinstance[0].estun['reset'] = False
            lockerinstance[0].lock.release()

    def readDOG(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        DOGv = lockerinstance[0].estunModbus['N-OT']
        lockerinstance[0].lock.release()
        return DOGv

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
            def getTerminal(terminal):
                term=self.dterminals[terminal]
                termv=self.dterminals[terminal +'v']
                paramdict = self.config['SERVOPARAMETERS']
                mask = int(self.invertedReducedMask(lockerinstance, term))
                value = paramdict.getint(str(term[0]))
                Byval = (value & mask) >> (term[1][1]*4)
                return dictKeyByVal(termv, Byval)[0]
            for val in self.dterminalTypes: terminals[getTerminal(str(val[0]))] = val
            result = dict(filter(lambda item: item[1] is not None,terminals.items()))
            return result

    def IOControl(self, lockerinstance):
        sparams = self.config['SERVOPARAMETERS']
        if not self.terminals:
            self.terminals = self.getIOTerminals(lockerinstance, True)
        ##terminals are like {'SHOM':(14,'I1')}
        ##these values are programmable in servocontroller
        buscontrol = {  14:self.BusCtrlInputNode1_14,15:self.BusCtrlInputNode1_15,
                        16:self.BusCtrlInputNode1_16,17:self.BusCtrlInputNode1_17,
                        39:self.BusCtrlInputNode1_39,40:self.BusCtrlInputNode1_40,
                        41:self.BusCtrlInputNode1_41,42:self.BusCtrlInputNode1_42}
        currentvalue = self.readParameter(lockerinstance, self.MODBUSIO)
        #current value is one byte with 8bits corresponding with inputs
        lockerinstance[0].lock.acquire()
        if not lockerinstance[0].estun['homing']: lockerinstance[0].estunModbus['N-CL'] = False
        if not lockerinstance[0].estun['step']: lockerinstance[0].estunModbus['P-CON'] = False
        lockerinstance[0].lock.release()
        for n, param in enumerate(self.dterminalTypes[:8]):
            #dterminalTypes is tuple of tuples of which terminal is which input/output
            #dterminals[0] -> (14,'I1')
            currentparameter = dictKeyByVal(self.terminals, param)[0]
            #currentparameter is key of terminal like 'SHOM' corresponding with dterminalTypes
            currentNode = buscontrol[param[0]]
            bitmask = 0b1 << n%4
            if not (sparams.getint(str(currentNode[0])) & bitmask):
                #buscontrol byte corresponding to actual input & it's bitmask
                #BusCtrlInputNode is internal variable of servo controller and possibility of external control of inputs depends on it 
                bitmask = 0b1 << n
                lockerinstance[0].lock.acquire()
                lockerinstance[0].estunModbus[currentparameter] = bool(currentvalue & bitmask)
                lockerinstance[0].lock.release()
            else:
                bitmask = 0b1 << n
                lockerinstance[0].lock.acquire()
                valuetoset = lockerinstance[0].estunModbus[currentparameter]
                lockerinstance[0].lock.release()
                ErrorEventWrite(lockerinstance,str(bin(currentvalue)))
                bitmask = ~bitmask & 0xFF
                valuetoseta = (currentvalue & bitmask) | (valuetoset << n)
                self.setParameter(lockerinstance, self.MODBUSIO, valuetoseta)
        servoOutputs = self.readParameter(lockerinstance, self.OutputSignalState)
        for n, param in enumerate(self.dterminalTypes[8:]):
            currentparameter = dictKeyByVal(self.terminals, param)
            if not currentparameter:
                continue
            else:
                currentparameter = currentparameter[0]
            bitmask = 0b1 << n
            lockerinstance[0].lock.acquire()
            lockerinstance[0].estunModbus[currentparameter] = bool(servoOutputs & bitmask)
            lockerinstance[0].lock.release()
        for n, bit in enumerate(self.__bits(self.readParameter(lockerinstance, self.InputSignalState))):
            key = 'I' + str(n+1)
            lockerinstance[0].lock.acquire()
            lockerinstance[0].estunModbus[key] = bit
            lockerinstance[0].lock.release()
        for n, bit in enumerate(self.__bits(self.readParameter(lockerinstance, self.OutputSignalState))[7:]):
            key = 'O' + str(n+1)
            lockerinstance[0].lock.acquire()
            lockerinstance[0].estunModbus[key] = bit
            lockerinstance[0].lock.release()

    def __bits(self, values = [8*False], le = False):
        if isinstance(values, list):
            if len(values) > 8:
                values = values[:8]
            result = 0b00000000
            if le: values = values[::-1]
            for i, val in enumerate(values):
                if val: result += pow(2,i)
            return result
        if isinstance(values, int):
            values &= 0b11111111
            result = []
            for i in range(8):
                power = pow(2,7-i)
                result.append(bool(values//power))
                values &= 0b11111111 ^ power
            if not le: result = result[::-1] 
            return result
            

    def __init__(self, lockerinstance, configFile, *args, **kwargs):
        self.control_switch = {
            'homing':self.homing,
            'step':self.step,
            'reset':self.resetAlarm,
            'DOG':self.readDOG,
            'IOControl':self.IOControl}
        self.timerhoming = None
        self.timerstep = None
        self.config = configparser.ConfigParser()
        self.servobak = configparser.ConfigParser()
        fileFeedback = self.config.read(configFile)
        self.terminals = {}
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
            #lockerinstance[0].estun['homing'] = lockerinstance[0].estun['step'] = lockerinstance[0].estun['reset'] = lockerinstance[0].estun['DOG'] = False
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


    