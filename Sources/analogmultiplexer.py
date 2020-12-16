from Sources.modbusTCPunits import ADAMDataAcquisitionModule
import configparser
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources.misc import BlankFunc
from Sources.StaticLock import BlankLocker

class AnalogMultiplexer(ADAMDataAcquisitionModule):
    def __init__(self, lockerinstance = BlankLocker, settingFilePath = '', *args, **kwargs):
        self.moduleName = "ADAM6052"
        self.config = configparser.ConfigParser()
        self.Filefeedback = self.config.read(settingFilePath)
        self.parameters = self.config
        try:
            with self.parameters['AnalogMultiplexer'] as AmuxParameters:
                self.IPAddress = AmuxParameters.get('IPAddress')
                self.moduleName = AmuxParameters.get('moduleName')
                self.Port = AmuxParameters.getint('Port')
                self.myOutput = AmuxParameters.getint('BindOutput')
            super().__init__(self.moduleName, self.IPAddress, self.Port, *args, **kwargs)
            self.currentState = self.getState()
        except:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].events['Error'] = True
            lockerinstance[0].errorlevel[10] = True
            lockerinstance[0].shared['Errors'] += '/nAnalog multiplexer init error - Error while reading config file'
            lockerinstance[0].lock.release()

    def __prohibitedBehaviour(self, lockerinstance = BlankLocker, action = BlankFunc, *args, **kwargs):
        self.getState(lockerinstance)
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
    
    def getState(self, lockerinstance = BlankLocker):
        try:
            self.currentState = self.read_coils(lockerinstance = lockerinstance, input = 'DO0', NumberOfCoils = 3)
            return self.currentState
        except:
            return -1

    def isBusy(self, lockerinstance = BlankLocker):
        self.getState(lockerinstance)
        if self.currentState[2]:
            return True
        if self.currentState[self.myOutput] or not any(self.currentState):
            return False
        else:
            return True

    def setPath(self, lockerinstance = BlankLocker):
        if not self.isBusy(lockerinstance) and not self.__prohibitedBehaviour(lockerinstance = lockerinstance, action = self.write_coil, args = ('DO'+str(self.myOutput), True)):
            try:
                self.write_coil(lockerinstance = lockerinstance, coil = 'DO'+str(self.myOutput), value = True)
            except:
                pass
        else:
            raise AnalogMultiplexerError(lockerinstance = lockerinstance, args = ('setPath() ', 'DO'+str(self.myOutput), ' is prohibited'))

    def resetPath(self, lockerinstance = BlankLocker):
        if self.getState(lockerinstance)[self.myOutput] and not self.isBusy(lockerinstance):
            try:
                self.write_coil(lockerinstance = lockerinstance, coil = 'DO'+str(self.myOutput), value = False)
            except:
                pass
        else:
            raise AnalogMultiplexerError(lockerinstance = lockerinstance, args = ('resetPath() ', 'DO'+str(self.myOutput), ' is prohibited'))

    def activatePath(self, lockerinstance = BlankLocker):
        if not self.isBusy(lockerinstance) and not self.__prohibitedBehaviour(lockerinstance = lockerinstance, action = self.write_coil, args = ('DO'+str(2), True)):
            try:
                self.write_coil(lockerinstance = lockerinstance, coil = 'DO'+str(2), value = True)
            except:
                pass
        else:
            raise AnalogMultiplexerError(lockerinstance = lockerinstance, args = ('activatePath() ', 'DO'+str(self.myOutput), ' is prohibited'))

    def releasePath(self, lockerinstance = BlankLocker):
        if not self.isBusy(lockerinstance) and not self.__prohibitedBehaviour(lockerinstance = lockerinstance, action = self.write_coil, args = ('DO'+str(2), False)):
            try:
                self.write_coil(lockerinstance = lockerinstance, coil = 'DO'+str(2), value = False)
            except:
                pass
        else:
            raise AnalogMultiplexerError(lockerinstance = lockerinstance, args = ('releasePath() ', 'DO'+str(self.myOutput), ' is prohibited'))

class MyMultiplexer(AnalogMultiplexer):
    def __init__(self, lockerinstance = BlankLocker, settingFilePath = '', *args, **kwargs):
        super().__init__(lockerinstance = lockerinstance, settingFilePath = settingFilePath, *args, **kwargs)
        lockerinstance[0].lock.acquire()
        lockerinstance[0].mux['Alive'] = True
        lockerinstance[0].lock.release()
        lockerinstance[0].muxloop(lockerinstance)

    def isBusy(self, lockerinstance = BlankLocker):
        result = super().isBusy(lockerinstance) 
        lockerinstance[0].lock.acquire()
        lockerinstance[0].mux['busy'] = result
        lockerinstance[0].lock.release()
        return result

    def getState(self, lockerinstance = BlankLocker):
        self.currentState = super().getState(lockerinstance)
        lockerinstance[0].lock.acquire()
        lockerinstance[0].mux['onpath'] = self.currentState[self.myOutput]
        if lockerinstance[0].mux['onpath']:
            lockerinstance[0].mux['ready'] = self.currentState[2]
        lockerinstance[0].lock.release()
        
    def __acquire(self, lockerinstance = BlankLocker): 
        if not self.isBusy(lockerinstance):
            if self.currentState[self.myOutput]:
                if self.currentState[2]:
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].mux['acquire'] = False
                    lockerinstance[0].lock.release()
                else:
                    self.activatePath(lockerinstance)
            else:
                self.setPath(lockerinstance)

    def __release(self, lockerinstance = BlankLocker):
        if self.currentState[self.myOutput]:
            if not self.currentState[2]:
                if self.currentState[self.myOutput]:
                    self.resetPath(lockerinstance)
                else:
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].mux['release'] = False
                    lockerinstance[0].lock.release()
            else:
                self.releasePath(lockerinstance)

    def MUXloop(self, lockerinstance = BlankLocker, *args, **kwargs):
        while True:
            lockerinstance[0].lock.acquire()
            self.Alive = lockerinstance[0].mux['Alive']
            lockerinstance[0].lock.release()
            if not self.Alive: break
            try:
                self.getState(lockerinstance)
            except:
                pass
            lockerinstance[0].lock.acquire()
            ack, rel = lockerinstance[0].mux['acquire'], lockerinstance[0].mux['release']
            lockerinstance[0].lock.release()
            if ack: self.__acquire(lockerinstance)
            if rel: self.__release(lockerinstance)

class AnalogMultiplexerError(Exception):
    def __init__(self, lockerinstance = BlankLocker, *args, **kwargs):
        self.args = args
        lockerinstance[0].lock.acquire()
        lockerinstance[0].shared['Errors'] += 'Analog multiplexer Error:\n' + ''.join(map(str, *args))
        lockerinstance[0].errorlevel[2] = True #High errorLevel
        lockerinstance[0].lock.release()