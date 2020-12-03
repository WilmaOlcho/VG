from modbusTCPunits import ADAMDataAcquisitionModule
import configparser
from TactWatchdog import TactWatchdog as WDT
from misc import BlankFunc
from StaticLock import SharedLocker

class AnalogMultiplexer(ADAMDataAcquisitionModule, SharedLocker):
    def __init__(self, settingFilePath, *args, **kwargs):
        self.config = configparser.ConfigParser()
        self.parameters = self.config.read(settingFilePath)
        try:
            with self.parameters['AnalogMultiplexer'] as AmuxParameters:
                self.IPAddress = AmuxParameters.get('IPAddress')
                self.moduleName = AmuxParameters.get('moduleName')
                self.Port = AmuxParameters.getint('Port')
                self.myOutput = AmuxParameters.getint('BindOutput')
        except:
            self.lock.acquire()
            self.events['Error'] = True
            self.errorlevel[10] = True
            self.shared['Errors'] += '/nAnalog multiplexer init error - Error while reading config file'
            self.lock.release()
        finally:
            super().__init__(self.moduleName, self.IPAddress, self.Port, *args, **kwargs)
            self.currentState = self.getState()

    def __prohibitedBehaviour(self, action = BlankFunc, *args, **kwargs):
        self.getState()
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
        self.currentState = self.read_coils('DO0',3)
        return self.currentState

    def isBusy(self):
        self.getState()
        if self.currentState[2]:
            return True
        if self.currentState[self.myOutput] or not any(self.currentState):
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
        self.lock.acquire()
        self.mux['Alive'] = True
        self.lock.release()
        self.MUXloop()

    def isBusy(self):
        result = super().isBusy() 
        self.lock.acquire()
        self.mux['busy'] = result
        self.lock.release()
        return result

    def getState(self):
        self.currentState = super().getState()
        self.lock.acquire()
        self.mux['onpath'] = self.currentState[self.myOutput]
        if self.mux['onpath']:
            self.mux['ready'] = self.currentState[2]
        self.lock.release()
        
    def _acquire(self): 
        if not self.isBusy():
            if self.currentState[self.myOutput]:
                if self.currentState[2]:
                    self.lock.acquire()
                    self.mux['acquire'] = False
                    self.lock.release()
                else:
                    self.activatePath()
            else:
                self.setPath()

    def _release(self):
        if self.currentState[self.myOutput]:
            if not self.currentState[2]:
                if self.currentState[self.myOutput]:
                    self.resetPath()
                else:
                    self.lock.acquire()
                    self.mux['release'] = False
                    self.lock.release()
            else:
                self.releasePath()

    def MUXloop(self, *args, **kwargs):
        while True:
            self.lock.acquire()
            self.Alive = self.mux['Alive']
            self.lock.release()
            if not self.Alive: break
            self.getState()
            self.lock.acquire()
            ack, rel = self.mux['acquire'], self.mux['release']
            self.lock.release()
            if ack: self._acquire()
            if rel: self._release()

class AnalogMultiplexerError(Exception, SharedLocker):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.lock.acquire()
        self.shared['Errors'] += 'Analog multiplexer Error:\n' + ''.join(map(str, *args))
        self.shared['Error'][2] = True #High errorLevel
        self.lock.release()