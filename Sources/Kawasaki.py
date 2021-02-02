from Sources.modbusTCPunits import KawasakiVG
from Sources.TactWatchdog import TactWatchdog as WDT
from functools import lru_cache
from threading import Thread, currentThread
import json

class RobotVG(KawasakiVG):
    def __init__(self, lockerinstance, configFile='', *args, **kwargs):
        while True:
            try:
                self.parameters = json.load(open(configFile))
            except:
                lockerinstance[0].lock.acquire()
                lockerinstance[0].events['Error'] = True
                lockerinstance[0].errorlevel[10] = True
                lockerinstance[0].shared['Errors'] += '/nRobotVG init error - Config file not found'
                lockerinstance[0].lock.release()
            try:
                self.IPAddress = self.parameters['RobotParameters']['IPAddress']
                self.Port = self.parameters['RobotParameters']['Port']
            except:
                lockerinstance[0].lock.acquire()
                lockerinstance[0].events['Error'] = True
                lockerinstance[0].errorlevel[10] = True
                lockerinstance[0].shared['Errors'] += '/nRobotVG init error - Error while reading config file'
                lockerinstance[0].lock.release()
            else:
                super().__init__(lockerinstance, self.IPAddress, self.Port, *args, **kwargs)
                self.Alive = True
                lockerinstance[0].lock.acquire()
                lockerinstance[0].robot['Alive'] = self.Alive
                lockerinstance[0].lock.release()
                self.IOtab = [32*[False],32*[False]]
                self.Robotloop(lockerinstance)
                break
            finally:
                lockerinstance[0].lock.acquire()
                letdie = lockerinstance[0].events['closeApplication']
                lockerinstance[0].lock.release()
                if letdie: break

    def Robotloop(self, lockerinstance):
        while self.Alive:
            self.IOControl(lockerinstance)
            lockerinstance[0].lock.acquire()
            positioncontrol, commandcontrol = lockerinstance[0].robot['PositionControl'], lockerinstance[0].robot['CommandControl']
            lockerinstance[0].lock.release()
            if positioncontrol: self.misc(lockerinstance)
            if commandcontrol: self.CommandControl(lockerinstance)
            self.ErrorCatching(lockerinstance)
            lockerinstance[0].lock.acquire()
            self.Alive = lockerinstance[0].robot['Alive']
            lockerinstance[0].lock.release()

    def ErrorCatching(self, lockerinstance):
        ##TODO There are statusRegisters for forbidden operation
        pass

    @lru_cache(maxsize = 16)
    def _splitdecimals(self, floatval):
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
            lockerinstance[0].lock.acquire()
            lockerinstance[0].robot['currentpos'] = RobotRegister[0]
            A, X = self._splitdecimals(lockerinstance[0].robot['A']), self._splitdecimals(lockerinstance[0].robot['X'])
            Y, Z = self._splitdecimals(lockerinstance[0].robot['Y']), self._splitdecimals(lockerinstance[0].robot['Z'])
            lockerinstance[0].robot['StatusRegister0'] = RobotRegister[9]
            lockerinstance[0].robot['StatusRegister1'] = RobotRegister[10]
            lockerinstance[0].robot['StatusRegister2'] = RobotRegister[11]
            lockerinstance[0].robot['StatusRegister3'] = RobotRegister[12]
            lockerinstance[0].robot['StatusRegister4'] = RobotRegister[13]
            lockerinstance[0].robot['StatusRegister5'] = RobotRegister[14]
            lockerinstance[0].robot['StatusRegister6'] = RobotRegister[15]
            lockerinstance[0].lock.release()
            if A[0] != RobotRegister[1]:
                self.write_register(lockerinstance, register = 'A', value = RobotRegister[1])
            if A[1] != RobotRegister[2]:
                self.write_register(lockerinstance, register = '00A', value = RobotRegister[2])
            if X[0] != RobotRegister[3]:
                self.write_register(lockerinstance, register = 'X', value = RobotRegister[3])
            if X[1] != RobotRegister[4]:
                self.write_register(lockerinstance, register = '00X', value = RobotRegister[4])
            if Y[0] != RobotRegister[5]:
                self.write_register(lockerinstance, register = 'Y', value = RobotRegister[5])
            if Y[1] != RobotRegister[6]:
                self.write_register(lockerinstance, register = '00Y', value = RobotRegister[6])
            if Z[0] != RobotRegister[7]:
                self.write_register(lockerinstance, register = 'Z', value = RobotRegister[7])
            if Z[1] != RobotRegister[8]:
                self.write_register(lockerinstance, register = '00Z', value = RobotRegister[8])

    def CommandControl(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        activecommand = lockerinstance[0].robot['activecommand']
        lockerinstance[0].lock.release()
        if not activecommand:
            lockerinstance[0].lock.acquire()
            homing, go = lockerinstance[0].robot['homing'], lockerinstance[0].robot['go']
            setoffset, goonce = lockerinstance[0].robot['setoffset'], lockerinstance[0].robot['goonce']
            lockerinstance[0].lock.release()
            if homing:
                self.write_register(lockerinstance, register = 'command', value = self.addresses['command_values']['homing'])
                lockerinstance[0].lock.acquire()
                lockerinstance[0].robot['activecommand'] = True
                lockerinstance[0].robot['homing'] = False
                lockerinstance[0].lock.release()
            if go:
                lockerinstance[0].lock.acquire()
                spos = lockerinstance[0].robot['setpos']
                lockerinstance[0].lock.release()
                self.write_register(lockerinstance, register = 'DestinationPositionNumber', value = spos)
                self.write_register(lockerinstance, register = 'command', value = self.addresses['command_values']['go'])
                lockerinstance[0].lock.acquire()
                lockerinstance[0].robot['activecommand'] = True
                lockerinstance[0].robot['go'] = False
                lockerinstance[0].lock.release()
            if setoffset:
                self.write_register(lockerinstance, register = 'command', value = self.addresses['command_values']['setoffset'])
                lockerinstance[0].lock.acquire()
                lockerinstance[0].robot['activecommand'] = True
                lockerinstance[0].robot['setoffset'] = False
                lockerinstance[0].lock.release()
            if goonce:
                self.write_register(lockerinstance, register = 'command', value = self.addresses['command_values']['goonce'])
                lockerinstance[0].lock.acquire()
                lockerinstance[0].robot['activecommand'] = True
                lockerinstance[0].robot['goonce'] = False
                lockerinstance[0].lock.release()
        else:
            if self.read_holding_registers(lockerinstance, registerToStartFrom = 'command') == 0:
                lockerinstance[0].lock.acquire()
                lockerinstance[0].robot['activecommand'] = False
                lockerinstance[0].lock.release()

    def __bits(self, values = [16*False], le = False):
        if isinstance(values, list):
            if len(values) > 16:
                values = values[:16]
            result = 0b0000000000000000
            if le: values = values[::-1]
            for i, val in enumerate(values):
                if val: result += pow(2,i)
            return result
        if isinstance(values, int):
            values &= 0b1111111111111111
            result = []
            for i in range(16):
                power = pow(2,15-i)
                result.append(bool(values//power))
                values &= 0b1111111111111111 ^ power
            if not le: result = result[::-1] 
            return result

    def __readcoils(self, lockerinstance, input = True):
        inputs = [] 
        inputs.extend(self.read_holding_registers(lockerinstance, registerToStartFrom = 'I1-16' if input else 'O1-16'))
        inputs.extend(self.read_holding_registers(lockerinstance, registerToStartFrom = 'I17-32'if input else 'O17-32'))
        somethingchanged = False
        output = ''
        direction = ('I' if input else 'O')
        IOtabdirection = (0 if input else 1)
        lockerinstance[0].lock.acquire()
        WDTActive = 'WDTsomethingchanged' in lockerinstance[0].wdt
        lockerinstance[0].lock.release()
        if not WDTActive and not input:
            EventManager.AdaptEvent(lockerinstance, input = 'somethingChanged', edge = 'rising', event = 'somethingchanged')
            WDT.WDT(lockerinstance, additionalFuncOnCatch = lambda obj = self, lock = lockerinstance: obj.__changedstate(lock), scale = 'm', limitval = 10, errToRaise = 'somethingchanged', eventToCatch= 'somethingchanged', noerror = True)
        for i, reg in enumerate(inputs):
            bits = self.__bits(reg)
            for j in range(16):
                signalnumber = i*16+j+1
                signal = direction + str(signalnumber)
                lockerinstance[0].lock.acquire()
                lockerinstance[0].GPIO[signal] = bits[j]
                lockerinstance[0].lock.release()
                if self.IOtab[IOtabdirection][signalnumber-1] != bits[j]:
                    self.IOtab[IOtabdirection][signalnumber-1] = bits[j]
                    somethingchanged = True
                    output += signal + ' '
        if not input and somethingchanged:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].events['OutputChangedByRobot'] = True
            lockerinstance[0].events['OutputsChangedByRobot'] += output + ' '
            lockerinstance[0].lock.release()

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
        lockerinstance[0].lock.acquire()
        lockerinstance[0].GPIO['somethingChanged'] = False
        lockerinstance[0].lock.release()

    def IOControl(self, lockerinstance):    
            self.__readcoils(lockerinstance)
            self.__readcoils(lockerinstance, input = False)

class EventManager():
    def __init__(self, lockerinstance, input = '', edge = None, event = ''):
        self.input = input
        self.edge = edge
        self.event = event
        lockerinstance[0].lock.acquire()
        self.state = lockerinstance[0].GPIO[self.input]
        self.Alive = lockerinstance[0].robot['Alive']
        self.name = currentThread().name
        lockerinstance[0].ect.append(self.name)
        lockerinstance[0].lock.release()
        self.loop(lockerinstance)

    def loop(self, lockerinstance):
        while self.Alive:
            lockerinstance[0].lock.acquire()
            self.Alive = lockerinstance[0].robot['Alive'] and self.name in lockerinstance[0].ect
            currentstate = lockerinstance[0].GPIO[self.input]
            lockerinstance[0].lock.release()
            if not self.edge:
                if currentstate:
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].events[self.event] = True
                    lockerinstance[0].lock.release()
                    break
            elif self.edge == 'rising':
                if self.state:
                    lockerinstance[0].lock.acquire()
                    self.state = lockerinstance[0].GPIO[self.input]
                    lockerinstance[0].lock.release()
                elif currentstate:
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].events[self.event] = True
                    lockerinstance[0].lock.release()
                    break
            elif self.edge == 'falling':
                if not self.state:
                    lockerinstance[0].lock.acquire()
                    self.state = lockerinstance[0].GPIO[self.input]
                    lockerinstance[0].lock.release()
                elif not currentstate:
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].events[self.event] = True
                    lockerinstance[0].lock.release()
                    break
            elif self.edge == 'toggle':
                if self.state != currentstate:
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].events[self.event] = True
                    lockerinstance[0].lock.release()
                    break
        lockerinstance[0].lock.acquire()
        if self.name in lockerinstance[0].ect: lockerinstance[0].ect.remove(self.name)
        lockerinstance[0].lock.release()
    
    @classmethod
    def AdaptEvent(cls, lockerinstance, input = '', edge = None, event = ''):
        lockerinstance[0].lock.acquire()
        ectActive = str('EventCatcher: ' + event) in lockerinstance[0].ect
        lockerinstance[0].lock.release()
        if not ectActive:
            EventThread = Thread(target = cls, args = (lockerinstance, input, edge, event,))
            EventThread.setName('EventCatcher: ' + event)
            EventThread.start()

    @classmethod
    def DestroyEvent(cls, lockerinstance, event = ''):
        eventname = 'EventCatcher: ' + event
        lockerinstance[0].lock.acquire()
        ectActive = eventname in lockerinstance[0].ect
        if ectActive: lockerinstance[0].ect.remove(eventname)
        lockerinstance[0].lock.release()
