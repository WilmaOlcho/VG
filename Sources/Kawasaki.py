from Sources.modbusTCPunits import Kawasaki
from Sources.TactWatchdog import TactWatchdog as WDT
from .common import EventManager, ErrorEventWrite, Bits, dictKeyByVal
from functools import lru_cache
import json
import time

class RobotVG(Kawasaki):
    def __init__(self, lockerinstance, configFile='', *args, **kwargs):
        self.bitconverter = Bits(len=16)
        self.Alive = True
        while self.Alive:
            try:
                with open(configFile) as Hfile:
                    self.parameters = json.load(Hfile)
            except:
                ErrorEventWrite(lockerinstance, 'RobotVG init error - Config file not found')
            else:
                try:
                    self.IPAddress = self.parameters['RobotParameters']['IPAddress']
                    self.Port = self.parameters['RobotParameters']['Port']
                except:
                    ErrorEventWrite(lockerinstance, 'RobotVG init error - Error while reading config file')
                else:
                    super().__init__(lockerinstance, self.IPAddress, self.Port, params = self.parameters['Registers'], *args, **kwargs)
                    with lockerinstance[0].lock:
                        lockerinstance[0].robot['Alive'] = self.Alive
                    self.IOtab = [32*[False],32*[False]]
                    self.Robotloop(lockerinstance)
                    print('robot breaks')
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
            self.StatusUpdate(lockerinstance)
            self.ErrorCatching(lockerinstance)

    def StatusUpdate(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].robot['handmode'] = lockerinstance[0].safety['RobotTeachMode']
            lockerinstance[0].robot['motors'] = lockerinstance[0].safety['DeadMan'] #deadman is true when motors are true becouse in hand mode motors are true only when deadman is pressed
            lockerinstance[0].robot['cycle'] = lockerinstance[0].GPIO[dictKeyByVal(self.parameters['systemIO'], "Cycle")]
            lockerinstance[0].robot['connection'] = self.is_socket_open()
            lockerinstance[0].robot['homepos'] = lockerinstance[0].robot['currentpos'] == 0

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
        for reg, key in zip(['CurrentPositionNumber',
                            'A','00A','X','00X','Y','00Y','Z','00Z',
                            'StatusRegister0', 'StatusRegister1', 
                            'StatusRegister2', 'StatusRegister3', 
                            'StatusRegister4', 'StatusRegister5',
                            'StatusRegister6'],
                            ['currentpos',
                            'A','A','X','X','Y','Y','Z','Z',
                            'StatusRegister0', 'StatusRegister1', 
                            'StatusRegister2', 'StatusRegister3', 
                            'StatusRegister4', 'StatusRegister5', 
                            'StatusRegister6']):
            readregister = []
            try:
                readregister = self.read_holding_registers(lockerinstance, registerToStartFrom = reg)
                time.sleep(0.05)
            except Exception as e:
                print(str(e))
            else:
                if len(reg) > 3 and readregister:
                    with lockerinstance[0].lock:
                        lockerinstance[0].robot[key] = int(readregister[0])
                elif readregister:
                    if len(reg) == 1:
                        lockerinstance[0].robot[key] = float(readregister[0])
                    else:
                        lockerinstance[0].robot[key] += float('0.'+str(readregister[0]))
                else:
                    print(reg, 'is incorrect')


    def __Command(self, lockerinstance, command = ''):
        command_u = command[:1].upper() + command[1:]
        commandevent = 'Robot'+command_u+'Complete'
        def funconstart(obj = self, lockerinstance = lockerinstance):
            obj.write_register(lockerinstance, register = 'command', value = obj.addresses['command_values'][command])
            with lockerinstance[0].lock:
                lockerinstance[0].robot['activecommand'] = True
            EventManager.AdaptEvent(lockerinstance, input = '-robot.activecommand', event = commandevent)
        def funconexceed(lockerinstance = lockerinstance):
            EventManager.DestroyEvent(lockerinstance, event = commandevent)
        WDT.WDT(lockerinstance, additionalFuncOnStart = funconstart, additionalFuncOnExceed = funconexceed, limitval = 30, scale = 's', errToRaise = 'Robot '+command_u+' time exceeded', eventToCatch = commandevent)

    def CommandControl(self, lockerinstance):
        activecommand = self.read_holding_registers(lockerinstance, registerToStartFrom = 'command')
        if not activecommand: activecommand.append(0)
        if not activecommand[0]:
            with lockerinstance[0].lock:
                homing, go, setoffset, goonce = [lockerinstance[0].robot[x] for x in ['homing', 'go', 'setoffset', 'goonce']]
                for x in ['activecommand','homing', 'go', 'setoffset', 'goonce']: lockerinstance[0].robot[x] = False
            if homing:
                self.__Command(lockerinstance, command = 'homing')
            if go:
                with lockerinstance[0].lock:
                    spos = int(lockerinstance[0].robot['setpos'])
                    stable = int(lockerinstance[0].robot['settable'])
                self.write_register(lockerinstance, register = 'DestinationPositionNumber', value = spos)
                self.write_register(lockerinstance, register = 'table', value = stable)
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
        with lockerinstance[0].lock:
            for i in range(1,33):
                output.append(lockerinstance[0].GPIO[direction+str(i)])
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
