from Sources.modbusTCPunits import ADAMDataAcquisitionModule
import json
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources import BlankFunc, ErrorEventWrite, Bits
import time

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
        except Exception as e:
            errmessage = 'Analog multiplexer init error - Error while reading config file ' + str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)

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
            with lockerinstance[0].lock:
                lockerinstance[0].mux['ready'] = self.currentState.bits[self.myOutput]
                lockerinstance[0].mux['Channel'] = (1 if bool(self.currentState.bits[0]) else 0) + (2 if bool(self.currentState.bits[1]) else 0)
            return self.currentState.bits
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
            except Exception as e:
                errmessage = 'AnalogMultiplexer Error - setPath Error' + str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
        else:
            raise AnalogMultiplexerError(lockerinstance, args = ('setPath() ', 'DO'+str(self.myOutput), ' is prohibited'))

    def resetPath(self, lockerinstance):
        if self.getState(lockerinstance)[self.myOutput] and not self.isBusy(lockerinstance):
            try:
                self.write_coil(lockerinstance, coil = 'DO'+str(self.myOutput), value = False)
            except Exception as e:
                errmessage = 'AnalogMultiplexer Error - resetPath Error' + str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
        else:
            raise AnalogMultiplexerError(lockerinstance, args = ('resetPath() ', 'DO'+str(self.myOutput), ' is prohibited'))

    def activatePath(self, lockerinstance):
        if not self.isBusy(lockerinstance) and not self.__prohibitedBehaviour(lockerinstance, action = self.write_coil, args = ('DO'+str(2), True)):
            try:
                self.write_coil(lockerinstance, coil = 'DO'+str(2), value = True)
            except Exception as e:
                errmessage = 'AnalogMultiplexer Error - activatePath Error' + str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
        else:
            raise AnalogMultiplexerError(lockerinstance, args = ('activatePath() ', 'DO'+str(self.myOutput), ' is prohibited'))

    def releasePath(self, lockerinstance):
        if not self.isBusy(lockerinstance) and not self.__prohibitedBehaviour(lockerinstance, action = self.write_coil, args = ('DO'+str(2), False)):
            try:
                self.write_coil(lockerinstance, coil = 'DO'+str(2), value = False)
            except Exception as e:
                errmessage = 'AnalogMultiplexer Error - releasePath Error' + str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
        else:
            raise AnalogMultiplexerError(lockerinstance, args = ('releasePath() ', 'DO'+str(self.myOutput), ' is prohibited'))

class LaserControl(ADAMDataAcquisitionModule):
    def __init__(self, lockerinstance, settingFilePath = '', *args, **kwargs):
        try:
            self.parameters = json.load(open(settingFilePath))
            self.LconParameters = self.parameters['LaserControl']
            self.IPAddress = self.LconParameters['IPAddress']
            self.moduleName = self.LconParameters['moduleName']
            self.Port = self.LconParameters['Port']
            self.Bits = Bits()
        except Exception as e:
            errmessage = 'LaserControl init error - Error while reading config file' + str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
        try:
            super().__init__(lockerinstance, moduleName = self.moduleName, address =  self.IPAddress, port = self.Port, *args, **kwargs)
            self.inputState = []
            self.currentState = self.getState(lockerinstance)
        except Exception as e:
            errmessage = 'LaserControl init error ' + str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)

    def getState(self, lockerinstance):
        try:
            state = []
            inputstate = []
            for coil in ['ResetError','LaserRequest','OpticalChannelbit0','OpticalChannelbit1','OpticalChannelbit2','OpticalChannelbit3']:
                state.append(self.read_coils(lockerinstance, input = 'DO' + str(self.LconParameters[coil])))
            for coil in ['LaserReady','LaserError','LaserAssigned','LaserIsOn','LaserWarning','ChillerWarning','ChillerError']:
                inputstate.append(self.read_coils(lockerinstance, input = 'DI' + str(self.LconParameters[coil])))
            with lockerinstance[0].lock:
                lockerinstance[0].lcon['LaserError'] = inputstate[1]
                lockerinstance[0].lcon['LaserWarning'] = inputstate[4]
                lockerinstance[0].lcon['ChillerError'] = inputstate[5]
                lockerinstance[0].lcon['ChillerWarning'] = inputstate[6]
                lockerinstance[0].lcon['LaserReady'] = inputstate[0]
                lockerinstance[0].lcon['LaserOn'] = inputstate[3]
                lockerinstance[0].lcon['LaserAssigned'] = inputstate[2]
            self.currentState = state
            self.inputState = inputstate
            return state
        except Exception as e:
            errmessage = "getState Error:\n"+ str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            #raise LaserControlError(lockerinstance, errstring = errmessage)

    def __prohibitedBehaviour(self, lockerinstance):
        with lockerinstance[0].lock:
            prohibited = lockerinstance[0].mux['busy']
        return prohibited  

    def request(self, lockerinstance):
        if not self.__prohibitedBehaviour(lockerinstance):
            try:
                self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['LaserRequest']), True)
                time.sleep(0.1)
            except Exception as e:
                errmessage = "SetChannel LaserRequest Error\n"+ str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)

    def release(self, lockerinstance):
        if not self.__prohibitedBehaviour(lockerinstance):
            try:
                self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['LaserRequest']), False)
                time.sleep(0.1)
            except Exception as e:
                errmessage = "SetChannel LaserRequest Error\n"+ str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)

    def acquireLightPath(self, lockerinstance):
        if not self.__prohibitedBehaviour(lockerinstance):
            self.request(lockerinstance)
            try:
                channel = self.Bits.Bits(self.LconParameters['MyOpticalChannel'])
                for i in range(4):
                    self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['OpticalChannelbit'+str(i)]), channel[i])
                time.sleep(0.1)
            except Exception as e:
                errmessage = "SetChannel OpticalChannelSetup Error\n"+ str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            self.release(lockerinstance)

    def releaseLightPath(self, lockerinstance):
        if not self.__prohibitedBehaviour(lockerinstance):
            try:
                channel = self.Bits(0)
                for i in range(4):
                    self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['OpticalChannelbit'+str(i)]), channel[i])
                time.sleep(0.1)
            except Exception as e:
                errmessage = "SetChannel OpticalChannelSetup Error\n"+ str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)

    def laserOn(self, lockerinstance):
        self.getState(lockerinstance)
        if not self.inputState[3] and not self.__prohibitedBehaviour(lockerinstance):
            self.resetError(lockerinstance)
            self.request(lockerinstance)
            try:
                self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['LaserOn']), True)
                time.sleep(0.1)
            except Exception as e:
                errmessage = "SetChannel ResetErrors Error\n"+ str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            self.release(lockerinstance)

    def resetError(self, lockerinstance):
        self.getState(lockerinstance)
        if self.inputState[1] and not self.__prohibitedBehaviour(lockerinstance):
            self.request(lockerinstance)
            try:
                self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['ResetError']), True)
                time.sleep(0.1)
            except Exception as e:
                errmessage = "SetChannel ResetErrors Error\n"+ str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            self.release(lockerinstance)
            try:
                self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['ResetError']), False)
                time.sleep(0.1)
            except Exception as e:
                errmessage = "SetChannel ResetErrors Error\n"+ str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)

    def StopLaser(self, lockerinstance):
        self.getState(lockerinstance)
        if not self.inputState[3] and not self.__prohibitedBehaviour(lockerinstance):
            self.resetError(lockerinstance)
            self.request(lockerinstance)
            try:
                self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['LaserOn']), False)
                time.sleep(0.1)
            except Exception as e:
                errmessage = "SetChannel ResetErrors Error\n"+ str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            self.release(lockerinstance)

    def SetChannel(self, lockerinstance):
        self.resetError(lockerinstance)
        self.laserOn(lockerinstance)

class MyMultiplexer(AnalogMultiplexer):
    def __init__(self, lockerinstance, settingFilePath = '', *args, **kwargs):
        self.Alive = True
        while self.Alive:
            try:
                super().__init__(lockerinstance, settingFilePath = settingFilePath, *args, **kwargs)
            except Exception as e:
                errstring = "MyMultiplexer init error" + str(e)
                ErrorEventWrite(lockerinstance, errstring, errorlevel = 10)
            else:
                with lockerinstance[0].lock:
                    lockerinstance[0].mux['Alive'] = self.Alive
                self.MUXloop(lockerinstance)
            finally:
                with lockerinstance[0].lock:
                    letdie = lockerinstance[0].events['closeApplication']
                    self.Alive = lockerinstance[0].mux['Alive']
                if letdie: break
        
    def isBusy(self, lockerinstance):
        result = super().isBusy(lockerinstance) 
        with lockerinstance[0].lock:
            lockerinstance[0].mux['busy'] = result
        return result

    def getState(self, lockerinstance):
        self.currentState = super().getState(lockerinstance)
        if isinstance(self.currentState,int):
            errstring = "\nMyMultiplexer.getState cant get state: returned -1"
            ErrorEventWrite(lockerinstance, errstring, errorlevel = 10)
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].mux['onpath'] = self.currentState[self.myOutput]
                if lockerinstance[0].mux['onpath']:
                    lockerinstance[0].mux['ready'] = self.currentState[2]
        
    def __acquire(self, lockerinstance): 
        if not self.isBusy(lockerinstance):
            if self.currentState[self.myOutput]:
                if self.currentState[2]:
                    with lockerinstance[0].lock:
                        lockerinstance[0].mux['acquire'] = False
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
                    with lockerinstance[0].lock:
                        lockerinstance[0].mux['release'] = False
            else:
                self.releasePath(lockerinstance)

    def MUXloop(self, lockerinstance, *args, **kwargs):
        while self.Alive:
            with lockerinstance[0].lock:
                self.Alive = lockerinstance[0].mux['Alive']
            if not self.Alive: break
            try:
                self.getState(lockerinstance)
            except:
                pass
            with lockerinstance[0].lock:
                ack, rel = lockerinstance[0].mux['acquire'], lockerinstance[0].mux['release']
            if ack: 
                try:
                    self.__acquire(lockerinstance)
                except Exception as e:
                    errstring = str(e)
                    ErrorEventWrite(lockerinstance, errstring, errorlevel = 10)
            if rel:
                try:
                    self.__release(lockerinstance)
                except Exception as e:
                    errstring = str(e)
                    ErrorEventWrite(lockerinstance, errstring, errorlevel = 10)

class MyLaserControl(LaserControl):
    def __init__(self, lockerinstance, settingFilePath = '', *args, **kwargs):
        self.Alive = True
        while self.Alive:
            try:
                super().__init__(lockerinstance, settingFilePath = settingFilePath, *args, **kwargs)
            except Exception as e:
                errstring = "\nMyLaserControl init error" + str(e)
                ErrorEventWrite(lockerinstance, errstring, errorlevel = 10)
            else:
                with lockerinstance[0].lock:
                    lockerinstance[0].lcon['Alive'] = self.Alive
                self.Lconloop(lockerinstance)
            finally:
                with lockerinstance[0].lock:
                    letdie = lockerinstance[0].events['closeApplication']
                if letdie: break

    def Lconloop(self, lockerinstance):
        while self.Alive:
            self.getState(lockerinstance)
            with lockerinstance[0].lock:
                setchannel = lockerinstance[0].lcon['SetChannel']
                if setchannel: lockerinstance[0].lcon['SetChannel'] = False
                startlaser = lockerinstance[0].lcon['LaserTurnOn']
                if startlaser: lockerinstance[0].lcon['LaserTurnOn'] = False
                stoplaser = lockerinstance[0].lcon['LaserTurnOff']
                if stoplaser: lockerinstance[0].lcon['LaserTurnOff'] = False
                resetlaser = lockerinstance[0].lcon['LaserReset']
                if resetlaser: lockerinstance[0].lcon['LaserReset'] = False
                self.Alive = lockerinstance[0].lcon['Alive']
            if not self.Alive: break
            if setchannel: self.SetChannel(lockerinstance)
            if startlaser: self.laserOn(lockerinstance)
            if stoplaser: self.StopLaser(lockerinstance)
            if resetlaser: self.resetError(lockerinstance)

class LaserControlError(Exception):
    def __init__(self, lockerinstance, *args, **kwargs):
        self.args = args
        errstring = 'Laser Control Error:' + ''.join(map(str, args))
        ErrorEventWrite(lockerinstance, errstring, errorlevel = 2)

class AnalogMultiplexerError(Exception):
    def __init__(self, lockerinstance, *args, **kwargs):
        self.args = args
        errstring = 'Analog multiplexer Error:' + ''.join(map(str, *args))
        ErrorEventWrite(lockerinstance, errstring, errorlevel = 2)
        