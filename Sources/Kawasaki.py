from modbusTCPunits import KawasakiVG
from TactWatchdog import TactWatchdog
from StaticLock import SharedLocker
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
        self.CommandControl()
        self.misc()

    def misc(self):
        cpos = self.read_holding_registers(self.addresses['CurrentPositionNumber'])
        self.lock.acquire()
        self.robot['currentpos'] = cpos

        self.lock.release()


    def CommandControl(self):
        self.lock.acquire()
        activecommand = self.robot['activecommand']
        self.lock.release()
        if not activecommand:
            self.lock.acquire()
            homing, go = self.robot['homing'], self.robot['go']
            self.lock.release()
            if homing:
                self.write_registers(self.addresses['command'], self.addresses['command_values']['homing'])
                self.lock.acquire()
                self.robot['activecommand'] = True
                self.robot['homing'] = False
                self.lock.release()
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
        else:
            if self.read_holding_registers(self.addresses['command']) == 0:
                self.lock.acquire()
                self.robot['activecommand'] = False

    def _bits(self, values = [16*False], le = False):
        if isinstance(values, list):
            if len(values) > 8:
                values = values[:8]
            result = 0b0000000000000000
            if le: values = values[::-1]
            for i, val in enumerate(values):
                print(i,val)
                if val: result += pow(2,i)
                print(result)
            return result
        if isinstance(values, int):
            values &= 0b11111111
            result = []
            for i in range(16):
                power = pow(2,7-i)
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
            outputs.append(self.read_holding_registers('O1-8'))
            outputs.append(self.read_holding_registers('O17-24'))
            for i, reg in enumerate(outputs):
                self.lock.acquire()
                bits = self._bits(reg, le = True)
                for j in range(16):
                    self.GPIO['O'+str(i*16+j+1)] = bits[j] 
                self.lock.release()
