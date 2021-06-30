from functools import reduce
import json
from logging import captureWarnings
from Sources import ErrorEventWrite, EventManager, Bits
from Sources.TactWatchdog import TactWatchdog as WDT

from pymodbus.client.sync import ModbusSerialClient


class Servo(ModbusSerialClient):
    def __init__(self, lockerinstance, jsonfile, *args, **kwargs):
        self.Alive = True
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
                        self.servoloop(lockerinstance)
            with lockerinstance[0].lock:
                self.Alive = lockerinstance[0].servo['Alive']
                closeapp = lockerinstance[0].events['closeApplication']
            if closeapp or not self.Alive:
                self.close()
                break

    def servoloop(self, lockerinstance):
        control = {'run':False, 'step':False, 'homing':False, 'stop':False, 'reset':False}
        while self.Alive:
            with lockerinstance[0].lock:
                for key in control.keys():
                    control[key] = True if lockerinstance[0].servo[key] else False
                    lockerinstance[0].servo[key] = False
                self.Alive = lockerinstance[0].servo['Alive']
            if control['homing']: self.homing(lockerinstance)
            if control['step']: self.step(lockerinstance)
            if control['reset']: self.reset(lockerinstance)
            if control['run']: self.run(lockerinstance)
            if control['stop']: self.stop(lockerinstance)
            self.IO(lockerinstance)

    def IO(self, lockerinstance):
        try:
            status = self.read_holding_registers(int(self.addresses['status'][0],16),unit=self.unit)
            if isinstance(status,Exception): raise Exception(str(status))
        except Exception as e:
            ErrorEventWrite(lockerinstance, 'Reading status from servo unit error: ' + str(e) )
        else:
            stbits = self.Bits(status.registers[0])
            ErrorEventWrite(lockerinstance, str(stbits))
            codes = self.settings['codes']
            notreadytoswitchon = self.checkcode(stbits,codes['notreadytoswitchon'])
            disabled = self.checkcode(stbits,codes['disabled'])
            readytoswitchon = self.checkcode(stbits,codes['readytoswitchon'])
            switchon = self.checkcode(stbits,codes['switchon'])
            operationenabled = self.checkcode(stbits,codes['operationenabled'])
            faultreactionactive = self.checkcode(stbits,codes['faultreactionactive'])
            fault = self.checkcode(stbits,codes['fault'])
            warning = self.checkcode(stbits,codes['warning'])
            positionreached = self.checkcode(stbits,codes['positionreached'])
            with lockerinstance[0].lock:
                servo = lockerinstance[0].servo
                servo['notreadytoswitchon'] = notreadytoswitchon
                servo['disabled'] = disabled
                servo['readytoswitchon'] = readytoswitchon
                servo['switchon'] = switchon
                servo['operationenabled'] = operationenabled
                servo['faultreactionactive'] = faultreactionactive
                servo['fault'] = fault
                servo['warning'] = warning
                servo['positionreached'] = positionreached


    def status(self, lockerinstance, literal):
        with lockerinstance[0].lock:
            result = lockerinstance[0].servo[literal]
        return result
    
    def currentmode(self, lockerinstance):
        try:
            addr = int(self.settings['addresses']['currentmode'][0],16)
            ret = self.read_holding_registers(addr, 1 ,unit = self.unit)
            assert(not isinstance(ret, Exception))
        except Exception as e:
            ErrorEventWrite(lockerinstance, "Servo currentmode returned exception: " + str(e) + str(ret))
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
            print(hex(addr), str(ret))
            assert(not isinstance(ret, Exception))
        except Exception as e:
            ErrorEventWrite(lockerinstance, "Servo command returned exception: " + str(e) + str(ret))


    def homing(self, lockerinstance):
        desiredmode = self.settings['modes']['homing'] & 0xffff
        modeready = self.changemode(lockerinstance, desiredmode)
        if modeready == desiredmode:
            if self.status(lockerinstance, "operationenabled"):
                self.command(lockerinstance, self.settings["commands"]["homingoperationstart"])


    def decode16bit2scomplement(self, _2s):
        if not isinstance(_2s, int): return
        if _2s & 0x80000000:
            return -((~_2s & 0xffffffff) +1)
        else:
            return _2s & 0xffffffff

    def changemode(self, lockerinstance, desiredmode):
        currentmode = self.currentmode() & 0xffff
        desiredmode &= 0xffff
        print(currentmode, desiredmode)
        with lockerinstance[0].lock:
            switchon = lockerinstance[0].servo['switchon']
            openabled = lockerinstance[0].servo["operationenabled"]
        if currentmode != desiredmode:
            while True:
                self.IO(lockerinstance)
                with lockerinstance[0].lock:
                    disabled = lockerinstance[0].servo['disabled']
                    fault = lockerinstance[0].servo['fault']
                if disabled or fault:
                    break
                else:
                    self.stop(lockerinstance)
                try:
                    ret = self.write_registers(int(self.settings['addresses']['setmode'],16), values = [desiredmode],unit=self.unit)
                    assert(not isinstance(ret, Exception))
                except Exception as e:
                    ErrorEventWrite(lockerinstance, "Servo changemode returned exception: " + str(e) + str(ret))
                else:
                    if switchon or openabled:
                        self.run(lockerinstance)
                    if openabled:
                        self.run(lockerinstance)
        return self.currentmode() & 0xffff


    def step(self, lockerinstance):
        """
        In pointtable positioning this method check the direction of
        shaft to reach desired point of table and drives motor there.

        """
        desiredmode = self.settings['modes']['pointtablepositioning'] & 0xffff
        modeready = self.changemode(lockerinstance, desiredmode)
        if modeready == desiredmode:
            if self.status(lockerinstance, "operationenabled"):
                with lockerinstance[0].lock:
                    stepnb = int(lockerinstance[0].servo['positionNumber'])
                assert(stepnb>0)
                
                try:
                    actualtableaddress = self.read_holding_registers(0x2d69, 1,unit=self.unit)
                    assert(not isinstance(actualtableaddress, Exception))
                except Exception as e:
                    ErrorEventWrite(lockerinstance, "Servo command returned exception: " + str(e) + str(actualtableaddress))
                else:
                    tableaddress = 0x2800 | (stepnb & 0xff)
                    actualtableaddress = 0x2800 | actualtableaddress.registers[0]
                    try:
                        actualtable = self.read_holding_registers(actualtableaddress, 9,unit=self.unit)
                        table = self.read_holding_registers(tableaddress, 9,unit=self.unit)
                        assert(not isinstance(table, Exception))
                    except Exception as e:
                        ErrorEventWrite(lockerinstance, "Servo command returned exception: " + str(e) + str(table) + str(actualtable))
                    else:
                        actualtable = actualtable.registers
                        table = table.registers
                        actualtabledata = reduce(lambda a, b: a<<16 | b , actualtable[1:3][::-1])
                        tabledata = reduce(lambda a, b: a<<16 | b , table[1:3][::-1])

                        CW = (self.decode16bit2scomplement(tabledata) - self.decode16bit2scomplement(actualtabledata)) > 180
                        if CW:
                            command = self.settings['commands']['positioningrotationstartCW']
                        else:
                            command = self.settings['commands']['positioningrotationstartCCW']
                        self.command(lockerinstance, command)
    

    def reset(self, lockerinstance):
        faultreset = self.settings['commands']['faultreset']
        _faultreset = map(lambda it: -it,faultreset)
        if self.status(lockerinstance, "fault"):
            self.command(lockerinstance, _faultreset)
            self.command(lockerinstance, faultreset)


    def stop(self, lockerinstance):
        command = []
        if self.status(lockerinstance, "operationenabled"):
            command = self.settings['commands']['disableoperation']
        if self.status(lockerinstance, "switchon"):
            command = self.settings['commands']['shutdown']
        self.command(lockerinstance, command)

        
    def run(self, lockerinstance):
        command = []
        if self.status(lockerinstance, "readytoswitchon") or self.status(lockerinstance, "disabled"):
            command = self.settings['commands']['switchon']
        if self.status(lockerinstance, "switchon"):
            command = self.settings['commands']['enableoperation']
        self.command(lockerinstance, command)


 