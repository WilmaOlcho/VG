from Sources.modbusTCPunits import Kawasaki
from .common import Bits, dictKeyByVal
from pywinauto import Application
import psutil
import json
import wmi, os, re
from time import sleep


import logging
_logger = logging.getLogger(__name__)

class AppController(Application):
    allow_magic_lookup = True
    def __init__(self, *args, **kwargs):
        self.WMI = wmi.WMI()
        self.processes = self.WMI.InstancesOf('Win32_Process')
        self.allow_magic_lookup = kwargs.pop("allow_magic_lookup",True)
        self.title = kwargs.pop("title",'')
        self.visibleonly = kwargs.pop('visible_only',False)
        name_re = kwargs.pop("Name_re",'')
        if name_re:
            self.Name = name_re
            self.PID = self.__GetPIDFromName(_re = True)
        else:
            self.Name = kwargs.pop("Name",'')
        if self.Name and not name_re:
            self.PID = self.__GetPIDFromName()
        else:
            PIDfromkwargs = kwargs.pop("PID",0)
            if PIDfromkwargs:
                self.PID = PIDfromkwargs
            self.Name = self.__GetNameFromPID()
        self.ProcessHandle = psutil.Process(self.PID)
        super().__init__(backend = kwargs.pop('backend','win32'))
        if self.PID:
            self.resume()
            self.connect(process = self.PID)
        if self.PID:
            if self.title:
                apptitles = [window.window_text() for window in self.windows()]
                title = list(filter(lambda t, self = self: re.findall(self.title, t),apptitles))
                if title: title=title[0]
                else: raise Exception()
                self.top = self.window(title = title, visible_only=self.visibleonly)
            else:
                self.top = self.top_window(visible_only=self.visibleonly)
        else:
            self.top =  None

    def __RetrieveValueFromProcess(self, KnownProcessValue, VariableName, ProcessValueToReturnName, **kwargs):
        def IsProcessValid(process, KnownProcessValue=KnownProcessValue, VariableName=VariableName):
            return re.findall(str(KnownProcessValue), str(process.Properties_(VariableName).Value))
        InstanceWeLookingFor = list(filter(IsProcessValid,self.processes))
        if InstanceWeLookingFor:
            InstanceWeLookingFor = InstanceWeLookingFor[0]
            if ProcessValueToReturnName == 'Name':
                return InstanceWeLookingFor.Name
            if ProcessValueToReturnName == 'ProcessId':
                return InstanceWeLookingFor.ProcessId
            return InstanceWeLookingFor.Properties_(ProcessValueToReturnName).Value
    
    def __GetPIDFromName(self, **kwargs):
        return self.__RetrieveValueFromProcess(self.Name,'Name','ProcessId', **kwargs)

    def __GetNameFromPID(self):
        return self.__RetrieveValueFromProcess(self.PID,'ProcessId','Name')

    def Properties_(self, propstring):
        return self.__RetrieveValueFromProcess(self.Name,'Name',propstring)


    def suspend(self):
        self.ProcessHandle.suspend()

    def resume(self):
        self.ProcessHandle.resume()
class RobotPlyty(Kawasaki):

    def __init__(self, lockerinstance, configFile='', *args, **kwargs):
        self.bitconverter = Bits(len=16)
        self.Alive = True
        while self.Alive:
            try:
                with open(configFile) as Hfile:
                    self.parameters = json.load(Hfile)
            except:
                _logger.debug('RobotPLYTY init error - Config file not found')
            else:
                try:
                    self.IPAddress = self.parameters['RobotParameters']['IPAddress']
                    self.Port = self.parameters['RobotParameters']['Port']
                except:
                    _logger.debug('RobotPLYTY init error - Error while reading config file')
                else:
                    super().__init__(lockerinstance, self.IPAddress, self.Port, params = self.parameters["Registers"], *args, **kwargs)
                    with lockerinstance[0].lock:
                        lockerinstance[0].robot2['Alive'] = self.Alive
                    try:
                        self.selfwindow = self.getselfwindow(lockerinstance)
                    except:
                        _logger.info('Przejecie okna glownego nie powiodlo sie')
                    else:
                        try:
                            with lockerinstance[0].lock:
                                scoutalive = lockerinstance[0].scout['Alive']
                            assert(scoutalive)
                            self.kdrawprocess = self.getkdrawprocess()
                            self.scout = self.scoutwindowhandle()
                        except:
                            _logger.info('Przejecie okna K-Draw nie powiodlo sie')
                        else:
                            try:
                                self.klasernet = self.klasernetwindowhandle()
                            except:
                                _logger.info('Przejecie okna KLaserNet nie powiodlo sie')
                            else:
                                try:
                                    self.LasernetPID = self.RunLaserNet()
                                except:
                                    _logger.info('Otwarcie okna LaserNet nie powiodlo sie')
                                else:
                                    try:
                                        self.Lasernet = AppController(PID = self.LasernetPID, title = ' LaserNet')
                                    except:
                                        _logger.info('Przejęcie okna LaserNet nie powiodlo sie')
                                    else:
                                        self.prtstr = ''
                                        self.selfwindow.set_focus()
                                        self.Robotloop(lockerinstance)
                finally:
                    with lockerinstance[0].lock:
                        self.Alive = lockerinstance[0].robot2['Alive']
                        closeapp = lockerinstance[0].events['closeApplication']
                    if closeapp or not self.Alive:
                        self.redirectlasertoPLYTY(lockerinstance)
                        break

    def RunLaserNet(self):
        _logger.info('RunLaserNet')
        param = self.parameters['LaserBeamRedirector']
        pcs = list(filter(lambda p,namestr=param['LaserNet']: namestr == p.Name, wmi.WMI().InstancesOf('Win32_Process')))
        if not pcs:
            startstr = 'start "'+param['LaserNet']+'" /D "'+param['LaserNetPath']+'" "'+param['LaserNetPath'] +param['LaserNet']+'"'
            os.popen(startstr)
            sleep(3)
            return self.RunLaserNet()
        else:
            PID = int(pcs[0].Properties_('ProcessId'))
            print('LaserNet PID:',PID)
            return PID


    def getkdrawprocess(self):
        return AppController(Name = 'Draw', title ='Draw ', backend = 'uia')


    def FreezeKdraw(self):
        if self.kdrawprocess:
            state = self.kdrawprocess.ProcessHandle.status()
            if state == 'running':
                print('FreezeKdraw')
                self.kdrawprocess.suspend()


    def ResumeKdraw(self):
        if self.kdrawprocess:
            state = self.kdrawprocess.ProcessHandle.status()
            if not state == 'running':
                print('ResumeKdraw',state)
                self.kdrawprocess.resume()


    def getselfwindow(self, lockerinstance):
        with lockerinstance[0].lock:
            if 'Window' in lockerinstance[0].shared['PID'].keys():
                selfwindow = lockerinstance[0].shared['PID']['Window']
            else:
                selfwindow = 0
        selfapp = AppController(PID = selfwindow, title='Spawanie')
        return selfapp.top

    def scoutwindowhandle(self):
        return self.kdrawprocess.top


    def klasernetwindowhandle(self):
        if self.scout:
            self.scout.TabControl.Drawing.select()
            self.scout.PlugIn.select()
            self.scout.IPC_Laser.select()
            klasernetapp = AppController(visible_only=False, backend = 'win32', Name_re="KLaser", title = 'KLaser')
            window = klasernetapp.top
            window.move_window(x=-1000)
            self.scout.TabControl.Auto.select()
            return window


    def ExControlOff(self):
        #if self.Lasernet:
        #    if self.Lasernet.status == 'running':
        #        self.Lasernet.top.TabControl.select("Control")
        #        if self.Lasernet.top.Button8.window_text() == 'ON':
        self.klasernet.ExternalControlOff.click()
        self.klasernet.AnalogControlOff.click()


    def Robotloop(self, lockerinstance):
        while self.Alive:
            with lockerinstance[0].lock:
                self.Alive = lockerinstance[0].robot2['Alive']
            if not self.Alive: break
            self.StatusUpdate(lockerinstance)
            self.InfoUpdate(lockerinstance)
            self.lasercontrol(lockerinstance)
            self.SendInfo(lockerinstance)


    def SendInfo(self, lockerinstance):
        with lockerinstance[0].lock:
            info = lockerinstance[0].robot2['Info']
        try:
            self.write_register(lockerinstance, register = 'info', value = int(info))
            #self.write_register(lockerinstance, register = 'est_time_VG', value = int(est_vg))
        except:
            pass


    def StatusUpdate(self, lockerinstance):
        try:
            currentstatus = str(self.read_holding_registers(lockerinstance, registerToStartFrom='status')[0])
            #est_plyty = self.read_holding_registers(lockerinstance, registerToStartFrom='est_time_PLYTY')[0]
        except Exception as e:
            pass
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].robot2['Status'] = currentstatus


    def InfoUpdate(self, lockerinstance):
        with lockerinstance[0].lock:
            if lockerinstance[0].program['handmodelaserrequire'] or (lockerinstance[0].program['running'] and lockerinstance[0].program['laserrequire']):
                lockerinstance[0].robot2['Info'] = dictKeyByVal(self.addresses['info_values'],'busy')
            elif lockerinstance[0].robot2['laserlocked']:
                lockerinstance[0].robot2['Info'] = dictKeyByVal(self.addresses['info_values'],'redirected')
            else:
                lockerinstance[0].robot2['Info'] = dictKeyByVal(self.addresses['info_values'],'nop')


    def lasercontrol(self, lockerinstance):
        with lockerinstance[0].lock:
            status = str(lockerinstance[0].robot2['Status'])
            info = str(lockerinstance[0].robot2['Info'])
            #est_vg = lockerinstance[0].robot2['Est_VG']
            #est_plyty = lockerinstance[0].robot2['Est_PLYTY']
        if self.addresses['info_values'][info] in ['busy'] and not self.addresses['status_values'][status] in ['welding']:
            self.redirectlasertoVG(lockerinstance)
        elif self.addresses['info_values'][info] in ['nop'] and self.addresses['status_values'][status] in ['laser_required']:
            self.redirectlasertoPLYTY(lockerinstance)


    def redirectlasertoPLYTY(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['AutostartOff'] = True
            lockerinstance[0].lcon['InternalControlSet'] = True
            lockerinstance[0].robot2['laserlocked'] = True
            lockerinstance[0].lcon['locklaserloop'] = True
        self.ExControlOff()
        self.FreezeKdraw()
        self.ExControlOff()


    def redirectlasertoVG(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].robot2['laserlocked'] = False
            lockerinstance[0].lcon['locklaserloop'] = False
        self.ResumeKdraw()
        self.klasernet.AnalogControlOn.click()
