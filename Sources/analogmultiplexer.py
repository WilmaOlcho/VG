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
        if action == self.write_coil:
            if self.currentState[0] and 'DO1' in args and True in args:
                return True
            if self.currentState[1] and 'DO0' in args and True in args:
                return True
            if not self.currentState[0] and not self.currentState[1] and 'DO2' in args and True in args:
                return True
        elif action == self.write_coils or action == self.write_register or action == self.write_registers:
            return True
        return False
    
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

    def resetPath(self):
        if self.getState()[self.myOutput]:
            if not self.isBusy():
                self.write_coil('DO'+str(self.myOutput), False)
