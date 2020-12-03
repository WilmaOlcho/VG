from ModbusTCPunits import KawasakiVG
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
        pass