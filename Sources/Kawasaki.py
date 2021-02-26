from Sources.modbusTCPunits import KawasakiVG
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources import EventManager, ErrorEventWrite, Bits
from functools import lru_cache
from threading import Thread, currentThread
import json

class RobotVG(KawasakiVG):
    def __init__(self, lockerinstance, configFile='', *args, **kwargs):
        self.bitconverter = Bits(len=16)
        self.Alive = True
        while self.Alive:
            try:
                self.parameters = json.load(open(configFile))
            except:
                ErrorEventWrite(lockerinstance, 'RobotVG init error - Config file not found')
            try:
                self.IPAddress = self.parameters['RobotParameters']['IPAddress']
                self.Port = self.parameters['RobotParameters']['Port']
            except:
                ErrorEventWrite(lockerinstance, 'RobotVG init error - Error while reading config file')
            else:
                super().__init__(lockerinstance, self.IPAddress, self.Port, *args, **kwargs)
                with lockerinstance[0].lock:
                    lockerinstance[0].robot['Alive'] = self.Alive
                self.IOtab = [32*[False],32*[False]]
                self.Robotloop(lockerinstance)
            finally:
                with lockerinstance[0].lock:
                    self.Alive = lockerinstance[0].robot['Alive']
                    closeapp = lockerinstance[0].events['closeApplication']
                if closeapp: break

    def Robotloop(self, lockerinstance):
        while self.Alive:
            self.IOControl(lockerinstance)
            with lockerinstance[0].lock:
                self.Alive = lockerinstance[0].robot['Alive']
                positioncontrol, commandcontrol = lockerinstance[0].robot['PositionControl'], lockerinstance[0].robot['CommandControl']
            if not self.Alive: break
            if positioncontrol: self.misc(lockerinstance)
            if commandcontrol: self.CommandControl(lockerinstance)
            self.ErrorCatching(lockerinstance)

    def ErrorCatching(self, lockerinstance):
        ##TODO There are statusRegisters for forbidden operation
        pass

    @lru_cache(maxsize = 64)
    def __splitdecimals(self, floatval):
        result = []
        result.append(int(floatval))
        result.append(int((floatval-result[0])*100))
        return result

    def misc(self, lockerinstance):
        RobotRegister = []
        for reg in ['CurrentPositionNumber','A','00A','X','00X','Y','00Y','Z','00Z',
                    'StatusRegister0',  'StatusRegister1',  'StatusRegister2', 
                    'StatusRegister3',  'StatusRegister4',  'StatusRegister5', 
                    'StatusRegister6']:
            RobotRegister.extend(self.read_holding_registers(lockerinstance, registerToStartFrom = reg))
        if len(RobotRegister) == 16:
            axisValues = {'A':[0,0], 'X':[0,0], 'Y':[0,0], 'Z':[0,0]}
            with lockerinstance[0].lock:
                lockerinstance[0].robot['currentpos'] = RobotRegister[0]
                for axis in axisValues.keys():
                    axisValues[axis] = self.__splitdecimals(lockerinstance[0].robot[axis])
                for i, status in enumerate(RobotRegister[9:][:7]):
                    lockerinstance[0].robot['StatusRegister' + str(i)] = status
            for i, register, axis in enumerate([[RobotRegister[1:][:8][x], [2*['A'],2*['X'],2*['Y'],2*['Z']][x]] for x in range(len(RobotRegister[1:][:8]))]):
                if i%2:
                    if axisValues[axis][0] != register:
                        self.write_register(lockerinstance, register = axis, value = register)
                else:
                    self.write_register(lockerinstance, register = '00'+axis, value = register)

    def __Command(self, lockerinstance, command = ''):
        command_u = command[:1].upper() + command[1:]
        commandevent = 'Robot'+command_u+'Complete'
        def funconstart(object = self, lockerinstance = lockerinstance):
            self.write_register(lockerinstance, register = 'command', value = object.addresses['command_values'][command])
            with lockerinstance[0].lock:
                lockerinstance[0].robot['activecommand'] = True
            EventManager.AdaptEvent(lockerinstance, input = '-robot.activecommand', event = commandevent)
        def funconexceed(lockerinstance = lockerinstance):
            EventManager.DestroyEvent(lockerinstance, event = commandevent)
        WDT.WDT(lockerinstance, additionalFuncOnStart = funconstart, additionalFuncOnExceed = funconexceed, limitval = 30, scale = 's', errToRaise = 'Robot '+command_u+' time exceeded', eventToCatch = commandevent)

    def CommandControl(self, lockerinstance):
        activecommand = self.read_holding_registers(lockerinstance, registerToStartFrom = 'command')
        if not activecommand:
            lockerinstance[0].lock.acquire()
            homing, go, setoffset, goonce = [lockerinstance[0].robot[x] for x in ['homing', 'go', 'setoffset', 'goonce']]
            for x in ['homing', 'go', 'setoffset', 'goonce']: lockerinstance[0].robot[x] = False
            lockerinstance[0].lock.release()
            if homing:
                self.__Command(lockerinstance, command = 'homing')
            if go:
                with lockerinstance[0].lock:
                    spos = lockerinstance[0].robot['setpos']
                self.write_register(lockerinstance, register = 'DestinationPositionNumber', value = spos)
                self.__Command(lockerinstance, command = 'go')
            if setoffset:
                self.__Command(lockerinstance, command = 'setoffset')
            if goonce:
                self.__Command(lockerinstance, command = 'goonce')

    def __readcoils(self, lockerinstance, input = True):
        inputs = [] 
        inputs.extend(self.read_holding_registers(lockerinstance, registerToStartFrom = 'I1-16' if input else 'O1-16'))
        inputs.extend(self.read_holding_registers(lockerinstance, registerToStartFrom = 'I17-32'if input else 'O17-32'))
        somethingchanged = False
        output = ''
        direction = ('I' if input else 'O')
        IOtabdirection = (0 if input else 1)
        with lockerinstance[0].lock:
            WDTActive = 'WDT: somethingchanged' in lockerinstance[0].wdt
        if not WDTActive and not input:
            def startcatchfunction(object = self, lockerinstance = lockerinstance):
                object.__changedstate(lockerinstance)
            EventManager.AdaptEvent(lockerinstance, input = 'somethingChanged', event = 'somethingchanged')
            WDT.WDT(lockerinstance, additionalFuncOnStart = startcatchfunction, additionalFuncOnCatch = startcatchfunction, scale = 'm', limitval = 10, errToRaise = 'somethingchanged', eventToCatch= 'somethingchanged', noerror = True)
        for i, reg in enumerate(inputs):
            bits = self.bitconverter.Bits(reg)
            for j in range(16):
                signalnumber = i*16+j+1
                signal = direction + str(signalnumber)
                with lockerinstance[0].lock:
                    lockerinstance[0].GPIO[signal] = bits[j]
                if self.IOtab[IOtabdirection][signalnumber-1] != bits[j]:
                    self.IOtab[IOtabdirection][signalnumber-1] = bits[j]
                    somethingchanged = True
                    output += signal + ' '
        if not input and somethingchanged:
            with lockerinstance[0].lock:
                lockerinstance[0].events['OutputChangedByRobot'] = True
                lockerinstance[0].events['OutputsChangedByRobot'] += output + ' '

    def __GPIO(self, lockerinstance, input = False):
        output = []
        direction = ('I' if input else 'O')
        lockerinstance[0].lock.acquire()
        for i in range(1,33):
            output.append(lockerinstance[0].GPIO[direction+str(i)])
        lockerinstance[0].lock.release()
        return output

    def __changedstate(self, lockerinstance):
        output = self.__GPIO(lockerinstance, input = False)
        for i in range(32):
            if i == 1-1 or i==27-1: #dedicated signals cant be picked up
                continue
            if output[i] != self.IOtab[1][i]: #single coil writing instead of 32
                self.write_coil(lockerinstance, Coil = 'DO' + str(i+1), value = output[i])
        with lockerinstance[0].lock:
            lockerinstance[0].GPIO['somethingChanged'] = False

    def IOControl(self, lockerinstance):    
            self.__readcoils(lockerinstance)
            self.__readcoils(lockerinstance, input = False)
