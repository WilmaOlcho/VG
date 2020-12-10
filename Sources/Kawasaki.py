from Sources.modbusTCPunits import KawasakiVG
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources.StaticLock import SharedLocker
from functools import lru_cache
import configparser

class RobotVG(KawasakiVG, SharedLocker):
    def __init__(self, configFile, *args, **kwargs):
        self.parameters = configparser.ConfigParser()
        self.filefeedback = self.parameters.read(configFile)
        self.timer = WDT()
        if len(self.filefeedback):
            try:
                with self.parameters['RobotParameters'] as RobotParameters:
                    self.IPAddress = RobotParameters.get('IPAddress')
                    self.Port = RobotParameters.getint('Port')
                    self.myOutput = RobotParameters.getint('BindOutput')
            except:
                self.lock.acquire()
                self.events['Error'] = True
                self.errorlevel[10] = True
                self.shared['Errors'] += '/nRobotVG init error - Error while reading config file'
                self.lock.release()
            finally:
                super().__init__(self.IPAddress, self.Port, *args, **kwargs)
                self.Alive = True
                self.lock.acquire()
                self.robot['Alive'] = self.Alive
                self.lock.release()
                self.Robotloop()
        else:
            self.lock.acquire()
            self.events['Error'] = True
            self.errorlevel[10] = True
            self.shared['Errors'] += '/nRobotVG init error - Config file not found'
            self.lock.release()
    
    def Robotloop(self):
        while self.Alive:
            self.IOControl()
            self.CommandControl()
            self.misc()
            self.ErrorCatching()
            self.lock.acquire()
            self.Alive = self.robot['Alive']
            self.lock.release()

    def ErrorCatching(self):
        ##TODO There are statusRegisters for forbidden operation
        pass

    @lru_cache(maxsize = 16)
    def _splitdecimals(self, floatval):
        result = []
        result.append(int(floatval))
        result.append(int((floatval-result[0])*100))
        return result

    def misc(self):
        RobotRegister = []
        for reg in ['CurrentPositionNumber','A','00A','X','00X','Y','00Y','Z','00Z',
                    'StatusRegister0',  'StatusRegister1',  'StatusRegister2', 
                    'StatusRegister3',  'StatusRegister4',  'StatusRegister5', 
                    'StatusRegister6']:
            RobotRegister.append(self.read_holding_registers(self.addresses[reg]))
        self.lock.acquire()
        self.robot['currentpos'] = RobotRegister[0]
        A, X = self._splitdecimals(self.robot['A']), self._splitdecimals(self.robot['X'])
        Y, Z = self._splitdecimals(self.robot['Y']), self._splitdecimals(self.robot['Z'])
        self.robot['StatusRegister0'] = RobotRegister[9]
        self.robot['StatusRegister1'] = RobotRegister[10]
        self.robot['StatusRegister2'] = RobotRegister[11]
        self.robot['StatusRegister3'] = RobotRegister[12]
        self.robot['StatusRegister4'] = RobotRegister[13]
        self.robot['StatusRegister5'] = RobotRegister[14]
        self.robot['StatusRegister6'] = RobotRegister[15]
        self.lock.release()
        if A[0] != RobotRegister[1]:
            self.write_registers(self.addresses['A'], RobotRegister[1])
        if A[1] != RobotRegister[2]:
            self.write_registers(self.addresses['00A'], RobotRegister[2])
        if X[0] != RobotRegister[3]:
            self.write_registers(self.addresses['X'], RobotRegister[3])
        if X[1] != RobotRegister[4]:
            self.write_registers(self.addresses['00X'], RobotRegister[4])
        if Y[0] != RobotRegister[5]:
            self.write_registers(self.addresses['Y'], RobotRegister[5])
        if Y[1] != RobotRegister[6]:
            self.write_registers(self.addresses['00Y'], RobotRegister[6])
        if Z[0] != RobotRegister[7]:
            self.write_registers(self.addresses['Z'], RobotRegister[7])
        if Z[1] != RobotRegister[8]:
            self.write_registers(self.addresses['00Z'], RobotRegister[8])

    def CommandControl(self):
        self.lock.acquire()
        activecommand = self.robot['activecommand']
        self.lock.release()
        if not activecommand:
            self.lock.acquire()
            homing, go = self.robot['homing'], self.robot['go']
            setoffset, goonce = self.robot['setoffset'], self.robot['goonce']
            self.lock.release()
            if homing:
                self.write_registers(self.addresses['command'], self.addresses['command_values']['homing'])
                self.lock.acquire()
                self.robot['activecommand'] = True
                self.robot['homing'] = False
                self.lock.release()
                self.timer = WDT.WDT(errToRaise = self.__class__ + 'RobotVG Homing time exceeded', errorlevel = 30, limitval = 20 )
            if go:
                self.lock.acquire()
                spos = self.robot['setpos']
                self.lock.release()
                self.write_registers(self.addresses['DestinationPositionNumber'], spos)
                self.write_registers(self.addresses['command'], self.addresses['command_values']['go'])
                self.lock.acquire()
                self.robot['activecommand'] = True
                self.robot['go'] = False
                self.lock.release()
                self.timer = WDT.WDT(errToRaise = self.__class__ + 'RobotVG moving time exceeded', errorlevel = 30, limitval = 20 )
            if setoffset:
                self.write_registers(self.addresses['command'], self.addresses['command_values']['setoffset'])
                self.lock.acquire()
                self.robot['activecommand'] = True
                self.robot['setoffset'] = False
                self.lock.release()
                self.timer = WDT.WDT(errToRaise = self.__class__ + 'RobotVG offsetting time exceeded', errorlevel = 30, limitval = 20 )
            if goonce:
                self.write_registers(self.addresses['command'], self.addresses['command_values']['goonce'])
                self.lock.acquire()
                self.robot['activecommand'] = True
                self.robot['goonce'] = False
                self.lock.release()
                self.timer = WDT.WDT(errToRaise = self.__class__ + 'RobotVG moving once time exceeded', errorlevel = 30, limitval = 20 )
        else:
            if self.read_holding_registers(self.addresses['command']) == 0:
                self.lock.acquire()
                self.robot['activecommand'] = False
                if self.timer.active: self.timer.Destroy()

    def _bits(self, values = [16*False], le = False):
        if isinstance(values, list):
            if len(values) > 16:
                values = values[:16]
            result = 0b0000000000000000
            if le: values = values[::-1]
            for i, val in enumerate(values):
                print(i,val)
                if val: result += pow(2,i)
                print(result)
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

    def IOControl(self):
        inputs = [] 
        inputs.append(self.read_holding_registers('I1-16'))
        inputs.append(self.read_holding_registers('I17-32'))
        for i, reg in enumerate(inputs):
            self.lock.acquire()
            bits = self._bits(reg, le = True)
            for j in range(16):
                self.GPIO['I'+str(i*16+j+1)] = bits[j] 
            self.lock.release()
        self.lock.acquire()
        somethingchanged = self.robot['somethingChaged']
        self.lock.release()
        def GPIOeights(startpoint):
            output = []
            self.lock.acquire()
            for i in range(16):
                output.append(self.GPIO['O'+str(i+startpoint)])
            self.lock.release()
            return output
        if somethingchanged:
            for i, reg in enumerate(['O1-16', 'O17-32']):
                self.write_register(reg, self._bits(GPIOeights(i*16+1), le = True))
            self.lock.acquire()
            self.robot['somethingChaged'] = False
            self.lock.release()
        else:
            outputs = [] 
            outputs.append(self.read_holding_registers('O1-16'))
            outputs.append(self.read_holding_registers('O17-32'))
            for i, reg in enumerate(outputs):
                self.lock.acquire()
                bits = self._bits(reg, le = True)
                for j in range(16):
                    output = 'O'+str(i*16+j+1)
                    if self.GPIO[output] != bits[j]:
                        self.events['OutputChangedByRobot'] = True
                        self.events['OutputsChangedByRobot'] += outputs + ' '
                        self.GPIO[output] = bits[j] 
                self.lock.release()
