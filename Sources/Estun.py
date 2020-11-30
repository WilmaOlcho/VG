import minimalmodbus
import serial
import configparser
import sys
import time
from TactWatchdog import TactWatchdog as WDT
from pronet_constants import Pronet_constants
from modbus_constants import Modbus_constants
from misc import BlankFunc, writeInLambda, dictKeyByVal
from Staticlock import SharedLocker

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

class MyEstun():
    class procedures(object):
        @staticmethod
        def homing(instance):
            if instance.timerhoming == None: instance.timerhoming = WDT.WDT(instance.shared, instance.lock, scale = 's',limitval = 30, errToRaise='Servo Homing Time exceeded', errorlevel=10)
            if instance.readDOG(instance):
                instance.WithLock(instance, lambda instance: writeInLambda(instance.shared['Estun']['homing'], False), instance)
                instance.WithLock(instance, lambda instance: writeInLambda(instance.shared['Events']['Estun']['homingComplete'], True), instance)
                instance.timer.Destruct()
            else:
                with lambda instance, stringval: instance.procedures.WithLock(instance, lambda instance, stringval: instance.shared['Estun']['MODBUS']['stringval']) as IsTrue:
                    if IsTrue(instance,'TGON'):
                        instance.WithLock(instance, lambda instance: writeInLambda(instance.shared['Estun']['MODBUS']['SHOM'], False), instance)
                    else:
                        instance.WithLock(instance, lambda instance: writeInLambda(instance.shared['Estun']['MODBUS']['SHOM'], True), instance)
            # homing key reaction:
            #   set homing input on servo for a while, resets when servo runs
            #   looking for DOG input for 30s
            #   DOG input destructs timer and close homing procedure 

        @staticmethod
        def step(instance):
            if instance.timerstep == None: instance.timerstep = WDT.WDT(instance.shared, instance.lock, scale = 's',limitval = 10, errToRaise='Servo Step Time exceeded', errorlevel=10)
            with lambda instance, stringval: instance.procedures.WithLock(instance, lambda instance, stringval: instance.shared['Estun']['MODBUS']['stringval']) as IsTrue:
                if IsTrue(instance,'TGON'):
                    instance.WithLock(instance, lambda instance: writeInLambda(instance.shared['Estun']['MODBUS']['PCON'], False), instance)
                else:
                    instance.WithLock(instance, lambda instance: writeInLambda(instance.shared['Estun']['MODBUS']['PCON'], True), instance)
                if IsTrue(instance,'COIN'):
                    instance.WithLock(instance, lambda instance: writeInLambda(instance.shared['Estun']['step'], False), instance)
                    instance.WithLock(instance, lambda instance: writeInLambda(instance.shared['Events']['Estun']['stepComplete'], True), instance)
                    instance.timer.Destruct()
            #step key reaction:
            #set PCON for a while, reset whne servo runs
            #looking for 10s for coin input
            #coin input destructs wdt timer and close step procedure

        @staticmethod
        def resetAlarm(instance):
            if instance.readParameter(instance,instance.CurrentAlarm) != 0:
                with instance.procedures.WithLock as lock:
                    instance.writeParameter(instance,instance.ClearCurrentAlarms, 0x01)
                    lock(instance, lambda instance: writeInLambda(instance.shared['Estun']['reset'], False), instance)
                    lock(instance, lambda instance: writeInLambda(instance.shared['Events']['Estun']['resetDone'], True), instance)

        @staticmethod
        def readDOG(instance):
            with lambda instance, stringval: instance.procedures.WithLock(instance, lambda instance, stringval: instance.shared['Estun']['MODBUS']['stringval']) as IsTrue:
                return IsTrue(instance,'ORG')

        @staticmethod
        def getIOTerminals(instance):
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
            with config['SERVOPARAMETERS'] as SERVOPARAMETERS:
                with instance.servo as srv:
                    getTerminal = lambda srv, terminal: dictKeyByVal(srv.dterminals[terminal+'v'],srv.InvertedReducedMask(srv.dterminals[terminal]) & SERVOPARAMETERS[str(srv.dterminals[terminal][0])])
                    for val in srv.dterminalTypes:
                        terminals[getTerminal(srv,str(val[0]))] = val
            return terminals

        @staticmethod
        def IOControl(instance):
            terminals = instance.procedures.getIOTerminals(instance)
            with instance.shared['Estun']['MODBUS'] as IOport:
                with instance.Servo as srv:
                    buscontrol = [  srv.BusCtrlInputNode1_14,srv.BusCtrlInputNode1_15,
                                    srv.BusCtrlInputNode1_16,srv.BusCtrlInputNode1_17,
                                    srv.BusCtrlInputNode1_39,srv.BusCtrlInputNode1_40,
                                    srv.BusCtrlInputNode1_41,srv.BusCtrlInputNode1_42]
                    for n, param in enumerate(srv.dterminalTypes[:8]):
                        if instance.config[buscontrol[n][0]] & srv.InvertedReducedMask(buscontrol[n]):
                            srv.setParameter(param,IOPort[dictKeyByVal(terminals,srv.dterminalTypes[n])])
                        else:
                            IOPort[dictKeyByVal(terminals,srv.dterminalTypes[n])] = srv.readParameter(param)
                    for n, param in enumerate(srv.dterminalTypes[8:]):
                            IOPort[dictKeyByVal(terminals,srv.dterminalTypes[n])] = srv.readParameter(param)

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.control_switch = {
            'procedure':{
                'homing':self.procedures.homing,
                'step':self.procedures.step,
                'reset':self.procedures.resetAlarm,
                'DOG':self.procedures.readDOG,
                'IOControl':self.procedures.IOcontrol}} 
        self.Servo = None
        self.config = configparser.ConfigParser()
        self.servobak = configparser.ConfigParser()

    def ServoLoop(self):
        with lambda instance, stringval: instance.WithLock(instance, lambda instance, stringval: instance.shared['Estun']['stringval']) as IsTrue:
            if IsTrue(self,'homing'): self.control_switch['homing'](self)
            if IsTrue(self,'step'): self.control_switch['step'](self)
            if IsTrue(self,'reset'): self.control_switch['reset'](self)
            if IsTrue(self,'DOG'): self.control_switch['DOG'](self)
            self.control_switch['DOGIOControl'](self)

    def ServoIsNone(self, config):
        with config['COMSETTINGS'] as COMSETTINGS:
            self.Servo = Estun( comport = COMSETTINGS['comport'],
                                slaveadress = COMSETTINGS['adress'],
                                protocol = COMSETTINGS['protocol'],
                                close_port_after_each_call = COMSETTINGS['close_port_after_each_call'] == 'True',
                                debug = COMSETTINGS['debug'] == 'True',
                                baud = COMSETTINGS.getboolean('baudrate'),
                                stopbits = COMSETTINGS.getboolean('stopbits'),
                                parity = COMSETTINGS['parity'],
                                bytesize = COMSETTINGS.getboolean('bytesize'))

    def ServoFirstAccess(self, Servo, servobak, config):
        bakparams = {'SERVOPARAMS':{}}
        for n in range(1000):
            data = Servo.read_register(n)
            if data is not None:
                bakparams['SERVOPARAMS'][str(n)] = data
        self.servobak.read_dict(bakparams)
        self.servobak.write('servobak'+ time.time() +'.ini')
        with config['SERVOPARAMETERS'] as SERVOPARAMETERS:
            for n, param in enumerate(SERVOPARAMETERS):
                    Servo.sendRegister(adress=int(param),value=int(SERVOPARAMETERS[param]))
                    self.WithLock(lambda: writeInLambda(self.shared['servoModuleFirstAccess'], False))

    @classmethod
    def Run(cli, *args, **kwargs):
        control = cli(*args, **kwargs)
        while True:   
            fileFeedback = control.config.read('servoEstun.ini')
            if fileFeedback == []:
                self.lock.acquire()
                shared['configurationError']=True
                shared['Errors'] += '/n Servo configuration file not found'
                shared['Error'][0] = True
                self.lock.release()
                break
            self.lock.acquire()
            Alive = self.shared['servoModule']
            self.lock.release()
            if Alive:
                if control.Servo is None:
                    control.ServoIsNone(fileFeedback)
                else:
                    self.lock.acquire(control.config)
                    firstAccess = shared['servoModuleFirstAccess']
                    self.lock.release()
                    if firstAccess == True:
                        control.ServoFirstAccess(control.Servo, control.servobak, control.config)
                    else:
                        control.ServoLoop()
            else:
                break






