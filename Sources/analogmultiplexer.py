from Sources.modbusTCPunits import ADAMDataAcquisitionModule
import json
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources.misc import BlankFunc

class AnalogMultiplexer(ADAMDataAcquisitionModule):
    def __init__(self, lockerinstance, settingFilePath = '', *args, **kwargs):
        try:
            self.parameters = json.load(open(settingFilePath))
            AmuxParameters = self.parameters['AnalogMultiplexer']
            self.IPAddress = AmuxParameters['IPAddress']
            self.moduleName = AmuxParameters['moduleName']
            self.Port = AmuxParameters['Port']
            self.myOutput = AmuxParameters['BindOutput']
            super().__init__(lockerinstance, moduleName =  self.moduleName, address =  self.IPAddress, port = self.Port, *args, **kwargs)
            self.currentState = self.getState(lockerinstance)
        except:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].events['Error'] = True
            lockerinstance[0].errorlevel[10] = True
            lockerinstance[0].shared['Errors'] += '/nAnalog multiplexer init error - Error while reading config file'
            lockerinstance[0].lock.release()

    def __prohibitedBehaviour(self, lockerinstance, action = BlankFunc, *args, **kwargs):
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
    
    def getState(self, lockerinstance):
        try:
            self.currentState = self.read_coils(lockerinstance, input = 'DO0', NumberOfCoils = 3)
            return self.currentState
        except:
            return -1

    def isBusy(self, lockerinstance):
        self.getState(lockerinstance)
        if self.currentState[2]:
            return True
        if self.currentState[self.myOutput] or not any(self.currentState):
            return False
        else:
            return True

    def setPath(self, lockerinstance):
        if not self.isBusy(lockerinstance) and not self.__prohibitedBehaviour(lockerinstance, action = self.write_coil, args = ('DO'+str(self.myOutput), True)):
            try:
                self.write_coil(lockerinstance, coil = 'DO'+str(self.myOutput), value = True)
            except:
                pass
        else:
            raise AnalogMultiplexerError(lockerinstance, args = ('setPath() ', 'DO'+str(self.myOutput), ' is prohibited'))

    def resetPath(self, lockerinstance):
        if self.getState(lockerinstance)[self.myOutput] and not self.isBusy(lockerinstance):
            try:
                self.write_coil(lockerinstance, coil = 'DO'+str(self.myOutput), value = False)
            except:
                pass
        else:
            raise AnalogMultiplexerError(lockerinstance, args = ('resetPath() ', 'DO'+str(self.myOutput), ' is prohibited'))

    def activatePath(self, lockerinstance):
        if not self.isBusy(lockerinstance) and not self.__prohibitedBehaviour(lockerinstance, action = self.write_coil, args = ('DO'+str(2), True)):
            try:
                self.write_coil(lockerinstance, coil = 'DO'+str(2), value = True)
            except:
                pass
        else:
            raise AnalogMultiplexerError(lockerinstance, args = ('activatePath() ', 'DO'+str(self.myOutput), ' is prohibited'))

    def releasePath(self, lockerinstance):
        if not self.isBusy(lockerinstance) and not self.__prohibitedBehaviour(lockerinstance, action = self.write_coil, args = ('DO'+str(2), False)):
            try:
                self.write_coil(lockerinstance, coil = 'DO'+str(2), value = False)
            except:
                pass
        else:
            raise AnalogMultiplexerError(lockerinstance, args = ('releasePath() ', 'DO'+str(self.myOutput), ' is prohibited'))

class MyMultiplexer(AnalogMultiplexer):
    def __init__(self, lockerinstance, settingFilePath = '', *args, **kwargs):
        super().__init__(lockerinstance, settingFilePath = settingFilePath, *args, **kwargs)
        lockerinstance[0].lock.acquire()
        lockerinstance[0].mux['Alive'] = True
        lockerinstance[0].lock.release()
        self.Alive = True
        self.MUXloop(lockerinstance)

    def isBusy(self, lockerinstance):
        result = super().isBusy(lockerinstance) 
        lockerinstance[0].lock.acquire()
        lockerinstance[0].mux['busy'] = result
        lockerinstance[0].lock.release()
        return result

    def getState(self, lockerinstance):
        self.currentState = super().getState(lockerinstance)
        if isinstance(self.currentState,int):
            errstring = "\nMyMultiplexer.getState cant get state: returned -1"
            lockerinstance[0].lock.acquire()
            if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring
            lockerinstance[0].lock.release()
        else:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].mux['onpath'] = self.currentState[self.myOutput]
            if lockerinstance[0].mux['onpath']:
                lockerinstance[0].mux['ready'] = self.currentState[2]
            lockerinstance[0].lock.release()
        
    def __acquire(self, lockerinstance): 
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

    def __release(self, lockerinstance):
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

    def MUXloop(self, lockerinstance, *args, **kwargs):
        while self.Alive:
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
            if ack: 
                try:
                    self.__acquire(lockerinstance)
                except:
                    pass
            if rel:
                try:
                    self.__release(lockerinstance)
                except:
                    pass

class AnalogMultiplexerError(Exception):
    def __init__(self, lockerinstance, *args, **kwargs):
        self.args = args
        lockerinstance[0].lock.acquire()
        lockerinstance[0].shared['Errors'] += 'Analog multiplexer Error:\n' + ''.join(map(str, *args))
        lockerinstance[0].errorlevel[2] = True #High errorLevel
        lockerinstance[0].lock.release()