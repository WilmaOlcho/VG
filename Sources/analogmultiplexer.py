from modbusTCPunits import ADAMDataAcquisitionModule
import configparser
from TactWatchdog import TactWatchdog as WDT
from misc import BlankFunc
from StaticLock import SharedLocker

class AnalogMultiplexer(ADAMDataAcquisitionModule, SharedLocker):
    def __init__(self, settingFilePath, *args, **kwargs):
        self.config = configparser.ConfigParser()
        self.parameters = self.config.read(settingFilePath)
        with self.parameters['AnalogMultiplexer'] as AmuxParameters:
            self.IPAddress = AmuxParameters['IPAddress']
            self.moduleName = AmuxParameters['moduleName']
            self.Port = AmuxParameters['Port']
            self.myOutput = AmuxParameters['BindOutput']
        super().__init__(self.moduleName, self.IPAddress, self.Port, *args, **kwargs)

    def __prohibitedBehaviour(self, action = BlankFunc, *args, **kwargs):
        self.currentState = self.getState()
        prohibited = False
        if action == self.write_coil:
            if not self.currentState[2]:
                if self.myOutput == 0:
                    if 'DO1' in args or self.currentState[1]:
                        prohibited = True
                elif self.myOutput == 1:
                    if 'DO0' in args or self.currentState[0]:
                        prohibited = True
            else:
                if 'DO1' in args or 'DO0' in args:
                    prohibited = True
        return prohibited  
    
    def getState(self):
        return self.read_coils('DO0',3)

    def isBusy(self):
        if self.getState()[2]:
            return True
        if self.getState()[self.myOutput] or not any(self.getState()):
            return False
        else:
            return True

    def setPath(self):
        if not self.isBusy() and not self.__prohibitedBehaviour(self.write_coil,'DO'+str(self.myOutput), True):
            self.write_coil('DO'+str(self.myOutput), True)
        else:
            raise AnalogMultiplexerError('setPath() ', 'DO'+str(self.myOutput), ' is prohibited')

    def resetPath(self):
        if self.getState()[self.myOutput] and not self.isBusy():
            self.write_coil('DO'+str(self.myOutput), False)
        else:
            raise AnalogMultiplexerError('resetPath() ', 'DO'+str(self.myOutput), ' is prohibited')

    def activatePath(self):
        if not self.isBusy() and not self.__prohibitedBehaviour(self.write_coil,'DO'+str(2), True):
            self.write_coil('DO'+str(2), True)
        else:
            raise AnalogMultiplexerError('activatePath() ', 'DO'+str(self.myOutput), ' is prohibited')

    def releasePath(self):
        if not self.isBusy() and not self.__prohibitedBehaviour(self.write_coil,'DO'+str(2), False):
            self.write_coil('DO'+str(2), False)
        else:
            raise AnalogMultiplexerError('releasePath() ', 'DO'+str(self.myOutput), ' is prohibited')

class MyMultiplexer(AnalogMultiplexer, SharedLocker):
    def __init__(self, settingFilePath, *args, **kwargs):
        super().__init__(settingFilePath, *args, **kwargs)

    def MUXloop(self, *args, **kwargs):
        pass



class AnalogMultiplexerError(Exception, SharedLocker):
    def __init__(self, *args, **kwargs):
        self.args = args
        SharedLocker.lock.acquire()
        SharedLocker.shared['Errors'] += 'Analog multiplexer Error:\n' + ''.join(map(str, *args))
        SharedLocker.shared['Error'][2] = True #High errorLevel
        SharedLocker.lock.release()