from Sources.modbusTCPunits import KawasakiVG
from Sources.TactWatchdog import TactWatchdog as WDT
from functools import lru_cache
import json

class RobotVG(KawasakiVG):
    def __init__(self, lockerinstance, configFile='', *args, **kwargs):
        try:
            self.parameters = json.load(open(configFile))
        except:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].events['Error'] = True
            lockerinstance[0].errorlevel[10] = True
            lockerinstance[0].shared['Errors'] += '/nRobotVG init error - Config file not found'
            lockerinstance[0].lock.release()
        self.timer = WDT()
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
            self.Robotloop(lockerinstance)

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
                self.timer = WDT.WDT(lockerinstance, errToRaise = self.__class__ + 'RobotVG Homing time exceeded', errorlevel = 30, limitval = 20 )
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
                self.timer = WDT.WDT(lockerinstance, errToRaise = self.__class__ + 'RobotVG moving time exceeded', errorlevel = 30, limitval = 20 )
            if setoffset:
                self.write_register(lockerinstance, register = 'command', value = self.addresses['command_values']['setoffset'])
                lockerinstance[0].lock.acquire()
                lockerinstance[0].robot['activecommand'] = True
                lockerinstance[0].robot['setoffset'] = False
                lockerinstance[0].lock.release()
                self.timer = WDT.WDT(lockerinstance, errToRaise = self.__class__ + 'RobotVG offsetting time exceeded', errorlevel = 30, limitval = 20 )
            if goonce:
                self.write_register(lockerinstance, register = 'command', value = self.addresses['command_values']['goonce'])
                lockerinstance[0].lock.acquire()
                lockerinstance[0].robot['activecommand'] = True
                lockerinstance[0].robot['goonce'] = False
                lockerinstance[0].lock.release()
                self.timer = WDT.WDT(lockerinstance,  errToRaise = self.__class__ + 'RobotVG moving once time exceeded', errorlevel = 30, limitval = 20 )
        else:
            if self.read_holding_registers(lockerinstance, registerToStartFrom = 'command') == 0:
                lockerinstance[0].lock.acquire()
                lockerinstance[0].robot['activecommand'] = False
                if self.timer.active: self.timer.Destroy()

    def _bits(self, values = [16*False], le = False):
        if isinstance(values, list):
            if len(values) > 16:
                values = values[:16]
            result = 0b0000000000000000
            if le: values = values[::-1]
            for i, val in enumerate(values):
                #print(i,val)
                if val: result += pow(2,i)
                #print(bin(result))
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

    def IOControl(self, lockerinstance):
        inputs = [] 
        inputs.extend(self.read_holding_registers(lockerinstance, registerToStartFrom = 'I1-16'))
        inputs.extend(self.read_holding_registers(lockerinstance, registerToStartFrom = 'I17-32'))
        for i, reg in enumerate(inputs):
            lockerinstance[0].lock.acquire()
            bits = self._bits(reg)
            for j in range(16):
                lockerinstance[0].GPIO['I'+str(i*16+j+1)] = bits[j] 
            lockerinstance[0].lock.release()
        lockerinstance[0].lock.acquire()
        somethingchanged = lockerinstance[0].GPIO['somethingChanged']
        lockerinstance[0].lock.release()
        def GPIOeights(startpoint):
            output = []
            lockerinstance[0].lock.acquire()
            for i in range(16):
                output.append(lockerinstance[0].GPIO['O'+str(i+startpoint)])
            lockerinstance[0].lock.release()
            return output
        if somethingchanged:
            for i, reg in enumerate(['O1-16', 'O17-32']):
                self.write_register(lockerinstance, register = reg, value = self._bits(GPIOeights(i*16+1), le = True))
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO['somethingChanged'] = False
            lockerinstance[0].lock.release()
        else:
            outputs = [] 
            outputs.extend(self.read_holding_registers(lockerinstance, registerToStartFrom = 'O1-16'))
            outputs.extend(self.read_holding_registers(lockerinstance, registerToStartFrom = 'O17-32'))
            for i, reg in enumerate(outputs):
                lockerinstance[0].lock.acquire()
                bits = self._bits(reg)
                for j in range(16):
                    output = 'O'+str(i*16+j+1)
                    if lockerinstance[0].GPIO[output] != bits[j]:
                        lockerinstance[0].events['OutputChangedByRobot'] = True
                        lockerinstance[0].events['OutputsChangedByRobot'] += output + ' '
                        lockerinstance[0].GPIO[output] = bits[j] 
                lockerinstance[0].lock.release()
