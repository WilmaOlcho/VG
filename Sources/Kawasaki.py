from Sources.modbusTCPunits import KawasakiVG
from Sources.TactWatchdog import TactWatchdog
from Sources.StaticLock import SharedLocker
import configparser

class RobotVG(KawasakiVG, SharedLocker):
    def __init__(self, configFile, *args, **kwargs):
        self.config = configparser.ConfigParser()
        self.parameters = self.config.read(configFile)
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
            self.lock.acquire()
            self.robot['Alive'] = True
            self.lock.release()
            self.Robotloop()
    
    def Robotloop(self):
        self.IOControl()

    def _bits(self, values = [8*False]):
        if isinstance(values, list):
            if len(values) > 8:
                values = values[:8]
            result = 0b00000000
            for i, val in enumerate(values):
                print(i,val)
                if val: result += pow(2,i)
                print(result)
            return result
        if isinstance(values, int):
            values &= 0b11111111
            result = []
            for i in range(8):
                power = pow(2,7-i)
                result.append(bool(values//power))
                values &= 0b11111111 ^ power
            result = result[::-1]
            return result

    def IOControl(self):
        inputs = [] 
        inputs.append(self.read_holding_registers('I1-8'))
        inputs.append(self.read_holding_registers('I9-16'))
        inputs.append(self.read_holding_registers('I17-24'))
        inputs.append(self.read_holding_registers('I25-32'))
        for i, reg in enumerate(inputs):
            self.lock.acquire()
            bits = self._bits(reg)
            for j in range(8):
                self.GPIO['I'+str(i*8+j+1)] = bits[j] 
            self.lock.release()
        self.lock.acquire()
        somethingchanged = self.robot['somethingChaged']
        self.lock.release()
        def GPIOeights(startpoint):
            for i in range(8):
                self.lock.acquire()
                output = self.GPIO['O'+str(i+startpoint)]
                self.lock.release()
                yield output
        if somethingchanged:
            for i, reg in enumerate(['O1-8', 'O9-16', 'O17-24', 'O25-32']):
                self.write_register(reg, self._bits(GPIOeights(i*8+1)))
            self.lock.acquire()
            self.robot['somethingChaged'] = False
            self.lock.release()
        else:
            outputs = [] 
            outputs.append(self.read_holding_registers('O1-8'))
            outputs.append(self.read_holding_registers('O9-16'))
            outputs.append(self.read_holding_registers('O17-24'))
            outputs.append(self.read_holding_registers('O25-32'))
            for i, reg in enumerate(outputs):
                self.lock.acquire()
                bits = self._bits(reg)
                for j in range(8):
                    self.GPIO['O'+str(i*8+j+1)] = bits[j] 
                self.lock.release()
