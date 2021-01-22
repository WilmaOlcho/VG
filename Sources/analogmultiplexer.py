from Sources.modbusTCPunits import ADAMDataAcquisitionModule
import json
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources.misc import BlankFunc, ErrorEventWrite
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

class LaserControl(ADAMDataAcquisitionModule):
    def __init__(self, lockerinstance, settingFilePath = '', *args, **kwargs):
        try:
            self.parameters = json.load(open(settingFilePath))
            self.LconParameters = self.parameters['LaserControl']
            self.IPAddress = self.LconParameters['IPAddress']
            self.moduleName = self.LconParameters['moduleName']
            self.Port = self.LconParameters['Port']
        except Exception as e:
            errmessage = 'LaserControl init error - Error while reading config file' + str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
        try:
            super().__init__(lockerinstance, moduleName = self.moduleName, address =  self.IPAddress, port = self.Port, *args, **kwargs)
            self.currentState = self.getState(lockerinstance)
        except Exception as e:
            errmessage = 'LaserControl init error ' + str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)

    def getState(self, lockerinstance):
        try:
            state = []
            state.append(self.read_coils(lockerinstance, input = 'DO' + str(self.LconParameters['ResetError'])))
            state.append(self.read_coils(lockerinstance, input = 'DO' + str(self.LconParameters['LaserRequest'])))
            state.append(self.read_coils(lockerinstance, input = 'DO' + str(self.LconParameters['OpticalChannelbit0'])))
            state.append(self.read_coils(lockerinstance, input = 'DO' + str(self.LconParameters['OpticalChannelbit1'])))
            state.append(self.read_coils(lockerinstance, input = 'DO' + str(self.LconParameters['OpticalChannelbit2'])))
            state.append(self.read_coils(lockerinstance, input = 'DO' + str(self.LconParameters['OpticalChannelbit3'])))
            self.currentState = state
            return self.currentState
        except Exception as e:
            errmessage = "getState Error:\n"+ str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            #raise LaserControlError(lockerinstance, errstring = errmessage)

    def __bits(self, values = [4*False], le = False):
        if isinstance(values, list):
            if len(values) > 4:
                values = values[:4]
            result = 0b0000
            if le: values = values[::-1]
            for i, val in enumerate(values):
                if val: result += pow(2,i)
            return result
        if isinstance(values, int):
            values &= 0b1111
            result = []
            for i in range(4):
                power = pow(2,3-i)
                result.append(bool(values//power))
                values &= 0b1111 ^ power
            if not le: result = result[::-1] 
            return result

    def __prohibitedBehaviour(self, lockerinstance, action = BlankFunc, *args, **kwargs):
        self.getState(lockerinstance)
        prohibited = False
        if action == self.write_coil:
            if args == ('DO'+str(self.LconParameters['LaserRequest']), True):
                if self.__bits(self.currentState[-4:]) != self.LconParameters['MyOpticalChannel']:
                    prohibited = True
            elif args == ('DO'+str(self.LconParameters['ResetError']), True):
                if not self.currentState[0]:
                    prohibited = True
        return prohibited  

    def SetChannel(self, lockerinstance):
        try:
            self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['LaserRequest']), False)
            time.sleep(0.1)
        except Exception as e:
            errmessage = "SetChannel LaserRequest Error\n"+ str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            #raise LaserControlError(lockerinstance, errstring = errmessage)
        try:
            channel = self.__bits(self.LconParameters['MyOpticalChannel'])
            self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['OpticalChannelbit0']), channel[0])
            self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['OpticalChannelbit1']), channel[1])
            self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['OpticalChannelbit2']), channel[2])
            self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['OpticalChannelbit3']), channel[3])
            time.sleep(0.1)
        except Exception as e:
            errmessage = "SetChannel OpticalChannelSetup Error\n"+ str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            #raise LaserControlError(lockerinstance, errstring = errmessage)
        if not self.__prohibitedBehaviour(lockerinstance, action = self.write_coil, args = ('DO'+str(self.LconParameters['LaserRequest']), True)):
            try:
                self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['LaserRequest']), True)
                time.sleep(0.1)
            except Exception as e:
                errmessage = "SetChannel LaserRequest Error\n"+ str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
                #raise LaserControlError(lockerinstance, errstring = errmessage)
        if not self.__prohibitedBehaviour(lockerinstance, action = self.write_coil, args = ('DO'+str(self.LconParameters['ResetError']), True)):
            try:
                self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['ResetError']), True)
                time.sleep(0.1)
            except Exception as e:
                errmessage = "SetChannel ResetErrors Error\n"+ str(e)
                ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
                #raise LaserControlError(lockerinstance, errstring = errmessage)
        try:
            self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['LaserRequest']), False)
            time.sleep(0.1)
        except Exception as e:
            errmessage = "SetChannel LaserRequest Error\n"+ str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            #raise LaserControlError(lockerinstance, errstring = errmessage)
        try:
            self.write_coil(lockerinstance, 'DO'+str(self.LconParameters['ResetError']), False)
            time.sleep(0.1)
        except Exception as e:
            errmessage = "SetChannel ResetError Error\n"+ str(e)
            ErrorEventWrite(lockerinstance, errmessage, errorlevel = 10)
            #raise LaserControlError(lockerinstance, errstring = errmessage)

class MyMultiplexer(AnalogMultiplexer):
    def __init__(self, lockerinstance, settingFilePath = '', *args, **kwargs):
        while True:
            try:
                super().__init__(lockerinstance, settingFilePath = settingFilePath, *args, **kwargs)
            except Exception as e:
                errstring = "MyMultiplexer init error" + str(e)
                ErrorEventWrite(lockerinstance, errstring, errorlevel = 10)
            else:
                lockerinstance[0].lock.acquire()
                lockerinstance[0].mux['Alive'] = True
                lockerinstance[0].lock.release()
                self.Alive = True
                self.MUXloop(lockerinstance)
                break
            finally:
                lockerinstance[0].lock.acquire()
                letdie = lockerinstance[0].events['closeApplication']
                lockerinstance[0].lock.release()
                if letdie: break
        
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
            ErrorEventWrite(lockerinstance, errstring, errorlevel = 10)
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
        while True:
            try:
                super().__init__(lockerinstance, settingFilePath = settingFilePath, *args, **kwargs)
            except Exception as e:
                errstring = "\nMyLaserControl init error" + str(e)
                ErrorEventWrite(lockerinstance, errstring, errorlevel = 10)
            else:
                lockerinstance[0].lock.acquire()
                lockerinstance[0].lcon['Alive'] = True
                lockerinstance[0].lock.release()
                self.Alive = True
                self.Lconloop(lockerinstance)
                break
            finally:
                lockerinstance[0].lock.acquire()
                letdie = lockerinstance[0].events['closeApplication']
                lockerinstance[0].lock.release()
                if letdie: break

    def Lconloop(self, lockerinstance):
        while self.Alive:
            lockerinstance[0].lock.acquire()
            setchannel = lockerinstance[0].lcon['SetChannel']
            self.Alive = lockerinstance[0].lcon['Alive']
            lockerinstance[0].lock.release()
            if not self.Alive: break
            if setchannel:
                self.SetChannel(lockerinstance)
                lockerinstance[0].lock.acquire()
                lockerinstance[0].lcon['SetChannel'] = False
                lockerinstance[0].lock.release()

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