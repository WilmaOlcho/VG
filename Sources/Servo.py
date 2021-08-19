from functools import reduce
import json
from Sources import ErrorEventWrite, EventManager, Bits
from Sources.TactWatchdog import TactWatchdog
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.factory import ExceptionResponse

import sys
sys.setrecursionlimit(10000)
from time import sleep


class Servo(ModbusSerialClient):
    resetting_after_redock = False


    def __init__(self, lockerinstance, jsonfile, *args, **kwargs):
        self.Alive = True
        self.lockservo = False
        with lockerinstance[0].lock:
            lockerinstance[0].servo['Alive'] = True
        while self.Alive:
            try:
                self.settings = json.load(open(jsonfile,'r'))
            except Exception as e:
                ErrorEventWrite(lockerinstance, "Servo.__init__ Error: Can't load json file " + str(e))
            else:
                try:
                    self.comsettings = self.settings['COMSETTINGS']
                except Exception as e:
                    ErrorEventWrite(lockerinstance, "Servo.__init__ Error: Can't use json file " + str(e))
                else:
                    try:
                        super().__init__(**self.comsettings)
                        assert(self.connect())
                    except Exception as e:
                        ErrorEventWrite(lockerinstance, "Servo.__init__ Error: Can't connect with external port " + str(e))
                    else:
                        self.Bits = Bits(len=16, LE = True)
                        self.addresses = self.settings['addresses']
                        self.unit = int(self.settings['unit'])
                        self.statusregisters=[
                            "notreadytoswitchon",
                            "disabled","readytoswitchon",
                            "switchon","operationenabled",
                            "faultreactionactive","fault",
                            "warning",'positionreached',
                            "homingattained","homepositionerror"
                        ]
                        try:
                            self.servoloop(lockerinstance)
                        except Exception as e:
                            ErrorEventWrite(lockerinstance, 'servo loop error:' + str(e))
            with lockerinstance[0].lock:
                self.Alive = lockerinstance[0].servo['Alive']
                closeapp = lockerinstance[0].events['closeApplication']
            if closeapp or not self.Alive:
                self.close()
                break

    def servoloop(self, lockerinstance):
        control = {'run':False, 'step':False, 'homing':False, 'stop':False, 'reset':False, "resetting_after_redock":False}
        def callback(l = lockerinstance):
            with l[0].lock:
                l[0].servo['resetting_after_redock'] = True
        while self.Alive:
            if not self.lockservo:
                for key in control.keys():
                    with lockerinstance[0].lock:
                        control[key] = lockerinstance[0].servo[key]
                        if key != "resetting_after_redock":
                            lockerinstance[0].servo[key] = False 
                if control['homing']: self.homing(lockerinstance)
                if control['step']: self.step(lockerinstance)
                if control['reset']: self.reset(lockerinstance)
                if control['run']: self.run(lockerinstance)
                if control['stop']: self.stop(lockerinstance)
                if control['resetting_after_redock']: self.reset_after_redocking(lockerinstance)
                EventManager.AdaptEvent(lockerinstance, count = 1, input = 'safety.TroleyReady',event='safety.TroleyReady', edge='falling', callback = callback)
            self.IO(lockerinstance)
            with lockerinstance[0].lock:
                self.Alive = lockerinstance[0].servo['Alive']

    def IO(self, lockerinstance):
        with lockerinstance[0].lock:
            self.lockservo = not lockerinstance[0].pistons['sensorSealDown']
            self.lockservo |= not lockerinstance[0].robot['homepos']
        if (self.lockservo
            and not self.status(lockerinstance,'disabled')):
            self.stop(lockerinstance)
        try:
            status = self.read_holding_registers(int(self.addresses['status'][0],16),unit=self.unit)
            currenttable = self.read_holding_registers(int(self.addresses['currenttable'][0],16),unit=self.unit)
            currentposition = self.read_holding_registers(0x2b2f,2,unit=self.unit)
            if isinstance(status,ExceptionResponse): raise Exception(str(status))
            if isinstance(currenttable,ExceptionResponse): raise Exception(str(currenttable))
            if isinstance(currentposition,ExceptionResponse): raise Exception(str(currentposition))
            if isinstance(status,Exception): raise Exception(str(status))
            if isinstance(currenttable,Exception): raise Exception(str(currenttable))
            if isinstance(currentposition,Exception): raise Exception(str(currentposition))
        except Exception as e:
            ErrorEventWrite(lockerinstance, 'Reading status from servo unit error: ' + str(e) )
        else:
            stbits = self.Bits(status.registers[0])
            codes = self.settings['codes']
            for register in self.statusregisters:
                registerstatus = self.checkcode(stbits,codes[register])
                with lockerinstance[0].lock:
                    lockerinstance[0].servo[register] = registerstatus
            pos = currenttable.registers[0]
            if not pos:
                _actual_pos = currentposition.registers[0]
                if _actual_pos == 7856: pos = 3
                elif _actual_pos == 24464: pos = 2
                else: pos = 0
            if pos:
                lockerinstance[0].servo["homepositionisknown"] = True
            with lockerinstance[0].lock:
                lockerinstance[0].servo['readposition'] = pos
                    
        with lockerinstance[0].lock:
            if not lockerinstance[0].troley['docked']:
                lockerinstance[0].servo["homepositionisknown"] = False
            

    def status(self, lockerinstance, key):
        with lockerinstance[0].lock:
            result = lockerinstance[0].servo[key]
        return result
    
    def currentmode(self, lockerinstance):
        try:
            addr = int(self.settings['addresses']['currentmode'][0],16)
            ret = self.read_holding_registers(addr, 1 ,unit = self.unit)
            if isinstance(ret, Exception): raise Exception(str(ret))
        except Exception as e:
            ErrorEventWrite(lockerinstance, "Servo currentmode returned exception: " + str(e))
        else:
            return self.decode16bit2scomplement(ret.registers[0])


    def checkcode(self, data, code):
        if not isinstance(data, list) or not data: return False
        datacheck = []
        data = data[::-1]
        for i in code:
            if i < 0:
                data[abs(i)-1] = not data[abs(i)-1]
            datacheck.append(data[abs(i)-1])
        return reduce(lambda item, nextitem:item & nextitem,datacheck)


    def command(self, lockerinstance, code):
        if not isinstance(code, list) or not code: return False
        value = self.Bits(0)
        for i in code:
            value[abs(i)-1] = i > 0
        try:
            addr = int(self.settings['addresses']['command'][0],16)
            ret = self.write_registers(addr, values = [self.Bits(value[::-1])],unit = self.unit)
            assert(not isinstance(ret, ExceptionResponse))
        except Exception as e:
            ErrorEventWrite(lockerinstance, "Servo command returned exception: " + str(e))
        sleep(0.1)


    def extractaddress(self, masterkey = "addresses", key = "command"):
        data = self.settings[masterkey][key][0]
        if isinstance(data,str): data =  int(data,16)
        return data


    def homing(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].servo['hominginprogress'] = True
        desiredmode = self.settings['modes']['homing'] & 0xff
        modeready = self.changemode(lockerinstance, desiredmode)
        if modeready == desiredmode:
            for i in range(100):
                self.run(lockerinstance)
                if self.status(lockerinstance, "operationenabled") and self.status(lockerinstance, "positionreached"): break
            homingsettings = self.settings['homing']
            lsBspeed = homingsettings['lsBspeed']
            msBspeed = homingsettings['msBspeed']
            lsBreturnspeed = homingsettings['lsBreturnspeed']
            msBreturnspeed = homingsettings['msBreturnspeed']
            method = homingsettings['method']
            if isinstance(method,str): method = int(method,16)
            homingspeedaddress = self.extractaddress(key = "homingspeed")
            homingmethodaddress = self.extractaddress(key = "homingmethod")
            #TODO errorcathing
            self.write_registers(homingmethodaddress, values = [method],unit=self.unit)
            self.write_registers(homingspeedaddress, values = [5,lsBspeed,msBspeed,lsBreturnspeed,msBreturnspeed],unit=self.unit)
            commandissent = False
            while True:
                if self.status(lockerinstance, "operationenabled") or commandissent:
                    if not commandissent:
                        self.command(lockerinstance, self.settings["commands"]["homingoperationstart"])
                        sleep(0.5)
                        commandissent = True
                    else:
                        EventManager.AdaptEvent(lockerinstance, count = 2, input = 'servo.homingattained',event='servo.homingattained', edge='rising')
                        def homereached(lockerinstance = lockerinstance):
                            with lockerinstance[0].lock:
                                lockerinstance[0].servo['hominginprogress'] = False
                                lockerinstance[0].servo['homepositionisknown'] = True
                        def homingfault(lockerinstance = lockerinstance):
                            with lockerinstance[0].lock:
                                lockerinstance[0].servo['hominginprogress'] = False
                        TactWatchdog.WDT(lockerinstance, limitval=30, scale = 's', additionalFuncOnExceed = homingfault,eventToCatch= "servo.homingattained", additionalFuncOnCatch= homereached, errToRaise= "Servo home positioning timeout error")
                        break
                else:
                    self.run(lockerinstance)

    def decode16bit2scomplement(self, _2s):
        if not isinstance(_2s, int): return
        if _2s & 0x80000000:
            return -((~_2s & 0xffffffff) +1)
        else:
            return _2s & 0xffffffff

    def changemode(self, lockerinstance, desiredmode):
        currentmode = self.currentmode(lockerinstance) & 0xff
        desiredmode &= 0xff
        if True:#currentmode != desiredmode:
            while True:
                if any([self.status(lockerinstance, key) for key in ['disabled','fault','readytoswitchon']]) :
                    break
                else:
                    self.stop(lockerinstance)
            try:
                ret = self.write_registers(int(self.settings['addresses']['setmode'][0],16), values = [desiredmode],unit=self.unit)
                assert(not isinstance(ret, ExceptionResponse))
            except Exception as e:
                ErrorEventWrite(lockerinstance, "Servo changemode returned exception: " + str(e))
        return self.currentmode(lockerinstance) & 0xff


    def step(self, lockerinstance):
        """
        In pointtable positioning this method check the direction of
        shaft to reach desired point of table and drives motor there.

        """
        with lockerinstance[0].lock:
            if 'WDT: servo.positionreached' in lockerinstance[0].wdt:
                return
            lockerinstance[0].servo['stepinprogress'] = True
        desiredmode = self.settings['modes']['pointtablepositioning'] & 0xff
        modeready = self.changemode(lockerinstance, desiredmode)
        if modeready == desiredmode:
            for i in range(100):
                self.run(lockerinstance)
                if self.status(lockerinstance, "operationenabled") and self.status(lockerinstance, "positionreached"): break
            if self.status(lockerinstance, "operationenabled") and self.status(lockerinstance, "homepositionisknown"):
                stepnb = int(self.status(lockerinstance, "positionNumber"))
                print(stepnb)
                assert stepnb>0
                try:
                    targetaddress = self.extractaddress(key="targettable")
                    self.write_registers(targetaddress,values = [stepnb], unit = self.unit)
                except Exception as e:
                    ErrorEventWrite(lockerinstance, "Servo command returned exception: " + str(e))
                try:
                    actualtableaddress = self.read_holding_registers(self.extractaddress(key="currenttable"), 1,unit=self.unit)
                    assert not isinstance(actualtableaddress, ExceptionResponse)
                except Exception as e:
                    ErrorEventWrite(lockerinstance, "Servo command returned exception: " + str(e))
                else:
                    tablebaseaddress = self.extractaddress(key="tablebaseaddress")
                    tableaddress = tablebaseaddress + (stepnb & 0xff)
                    actualtableaddress = tablebaseaddress + actualtableaddress.registers[0]
                    try:
                        table = self.read_holding_registers(tableaddress, 9,unit=self.unit)
                        table = table.registers
                        tabledata = reduce(lambda a, b: a<<16 | b , table[1:3][::-1])
                    except Exception as e:
                        ErrorEventWrite(lockerinstance, "Servo command returned exception: " + str(e))
                    else:
                        if actualtableaddress > tablebaseaddress:
                            try:
                                actualtable = self.read_holding_registers(actualtableaddress, 9,unit=self.unit)
                                actualtable = actualtable.registers
                                actualtabledata = reduce(lambda a, b: a<<16 | b , actualtable[1:3][::-1])
                                CW = (self.decode16bit2scomplement(tabledata) - self.decode16bit2scomplement(actualtabledata)) > 180
                            except Exception as e:
                                ErrorEventWrite(lockerinstance, "Servo command returned exception: " + str(e))
                        else:
                            CW=True
                        if CW:
                            command = self.settings['commands']['positioningrotationstartCW']
                            print("CW")
                        else:
                            command = self.settings['commands']['positioningrotationstartCCW']
                            print("CCW")
                        self.command(lockerinstance, command)
                        EventManager.AdaptEvent(lockerinstance, count = 2, input = 'servo.positionreached',event='servo.positionreached', edge='rising')
                        def posreached(lockerinstance = lockerinstance):
                            with lockerinstance[0].lock:
                                lockerinstance[0].servo['stepinprogress'] = False
                        TactWatchdog.WDT(lockerinstance, limitval=30, scale = 's', additionalFuncOnExceed = posreached,eventToCatch= "servo.positionreached", additionalFuncOnCatch= posreached, errToRaise= "Servo positioning timeout error")
                        
            elif not self.status(lockerinstance, "homepositionisknown"):
                ErrorEventWrite(lockerinstance, "Homing required")
    

    def reset(self, lockerinstance):
        faultreset = self.settings['commands']['faultreset']
        _faultreset = map(lambda it: -it,faultreset)
        if self.status(lockerinstance, "fault") or self.status(lockerinstance, "warning"):
            self.command(lockerinstance, _faultreset)
            self.command(lockerinstance, faultreset)
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].servo['resetting_after_redock'] = False


    def reset_after_redocking(self, lockerinstance):
        if self.status(lockerinstance, "fault"):
            def faultreset(obj = self, lock = lockerinstance):
                def raisereset(l = lock):
                    with l[0].lock:
                        l[0].safety['ResetServo'] = True
                def releasereset(l=lock):
                    with l[0].lock:
                        l[0].safety['ResetServo'] = False
                TactWatchdog.WDT(lock, errToRaise = 'reset_after_redocking0', additionalFuncOnStart = raisereset, additionalFuncOnExceed = releasereset, noerror = True, scale = 's',limitval = 1)
                def callback(o = obj, l = lock):
                    TactWatchdog.WDT(l, errToRaise = 'reset_after_redocking2', additionalFuncOnExceed = lambda _o = o, _l = l: _.reset(_l), noerror = True, scale = 's', limitval = 10)
                EventManager.AdaptEvent(lock, count = 1, input = 'safety.ServoSupplied',event='safety.ServoSupplied', edge='rising', callback = callback)
            TactWatchdog.WDT(lockerinstance, errToRaise = 'reset_after_redocking3', additionalFuncOnStart = faultreset ,additionalFuncOnExceed = lambda _o = self, _l = lockerinstance: _o.reset_after_redocking(_l), noerror = True, scale = 's', limitval = 5)

    def stop(self, lockerinstance):
        command = []
        if self.status(lockerinstance, "operationenabled"):
            command = self.settings['commands']['disableoperation']
        if self.status(lockerinstance, "switchon"):
            command = self.settings['commands']['shutdown']
        self.command(lockerinstance, command)
        self.IO(lockerinstance)


    def run(self, lockerinstance):
        command = []
        if (self.status(lockerinstance, "readytoswitchon")
            or self.status(lockerinstance, "disabled")):
            command = self.settings['commands']['switchon']
        if self.status(lockerinstance, "switchon"):
            command = self.settings['commands']['enableoperation']
        self.command(lockerinstance, command)
        self.IO(lockerinstance)

 