from Sources.modbusTCPunits import Kawasaki, KawasakiPLYTYParams

from Sources.TactWatchdog import TactWatchdog as WDT

from .common import EventManager, ErrorEventWrite, Bits, dictKeyByVal

from functools import lru_cache

from threading import Thread, currentThread

from pywinauto import Application

import psutil

import json


class RobotPlyty(Kawasaki):

    def __init__(self, lockerinstance, configFile='', *args, **kwargs):

        self.bitconverter = Bits(len=16)

        self.Alive = True

        while self.Alive:

            try:

                with open(configFile) as Hfile:

                    self.parameters = json.load(Hfile)

            except:

                ErrorEventWrite(lockerinstance, 'RobotPLYTY init error - Config file not found')

            else:

                try:

                    self.IPAddress = self.parameters['RobotParameters']['IPAddress']

                    self.Port = self.parameters['RobotParameters']['Port']

                except:

                    ErrorEventWrite(lockerinstance, 'RobotPLYTY init error - Error while reading config file')

                else:

                    super().__init__(lockerinstance, self.IPAddress, self.Port, params = KawasakiPLYTYParams(), *args, **kwargs)

                    with lockerinstance[0].lock:

                        lockerinstance[0].robot2['Alive'] = self.Alive

                    self.selfwindow = self.getselfwindow(lockerinstance)

                    self.scout = self.scoutwindowhandle()

                    self.kdrawprocess = self.getkdrawprocess()

                    self.klasernet = self.klasernetwindowhandle()

                    self.prtstr = ''

                    self.Robotloop(lockerinstance)

                finally:

                    with lockerinstance[0].lock:

                        self.Alive = lockerinstance[0].robot2['Alive']

                        closeapp = lockerinstance[0].events['closeApplication']

                    if closeapp: break


    def getkdrawprocess(self):

        import wmi

        import re

        WMI = wmi.WMI()

        processes = WMI.InstancesOf('Win32_Process')

        KdrawInstance = list(filter(lambda _:re.findall('Draw', _.Properties_('Name').Value),processes))

        if KdrawInstance:

            KdrawInstance = KdrawInstance[0]

            KdrawprocessId = KdrawInstance.Properties_('ProcessId').Value

            return psutil.Process(KdrawprocessId)

        else:

            return None



    def FreezeKdraw(self):

        if self.kdrawprocess:

            print('FreezeKdraw')
            self.kdrawprocess.suspend()



    def ResumeKdraw(self):

        if self.kdrawprocess:

            print('ResumeKdraw')

            self.kdrawprocess.resume()



    def getselfwindow(self, lockerinstance):
        while True:
            with lockerinstance[0].lock:
                selfwindowalive = lockerinstance[0].console['Alive']
            if selfwindowalive: break
        selfapp = Application().connect(title_re=".*Spawanie.*")

        return selfapp.window(title_re=".*Spawanie.*")



    def scoutwindowhandle(self):

        scoutapp = Application(backend="uia").connect(title_re=".*Draw.*")

        return scoutapp.window(title_re=".*Draw.*")



    def klasernetwindowhandle(self):

        self.scout.TabControl.Drawing.select()

        self.scout.PlugIn.select()

        self.scout.IPC_Laser.select()

        klasernetapp = Application().connect(title_re=".*KLaser.*")

        window = klasernetapp.window(title_re=".*KLaser.*")

        window.move_window(x=-1000)

        self.scout.TabControl.Auto.select()
        return window



    def ExControlOff(self):

        self.klasernet.set_focus()

        self.klasernet.ExternalControlOff.click()

        self.selfwindow.set_focus()



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

            currentstatus = self.read_holding_registers(lockerinstance, registerToStartFrom='status')[0]

            #est_plyty = self.read_holding_registers(lockerinstance, registerToStartFrom='est_time_PLYTY')[0]

        except Exception as e:
            print(str(e))

        else:

            with lockerinstance[0].lock:

                lockerinstance[0].robot2['Status'] = currentstatus

                #lockerinstance[0].robot2['Est_PLYTY'] = est_plyty

                info = lockerinstance[0].robot2['Info']

                #est_vg = lockerinstance[0].robot2['Est_VG']

            nprtstr = "BETON: {}, PLYTY: {}".format(self.params['info_values'][info],self.params['status_values'][currentstatus])

            if nprtstr != self.prtstr:
                    
                self.prtstr = nprtstr
            
                print(nprtstr)

            



    def InfoUpdate(self, lockerinstance):

        with lockerinstance[0].lock:

            if lockerinstance[0].program['handmodelaserrequire'] or (lockerinstance[0].program['running'] and lockerinstance[0].program['laserrequire']):

                lockerinstance[0].robot2['Info'] = dictKeyByVal(self.params['info_values'],'busy')

            elif lockerinstance[0].robot2['laserlocked']:

                lockerinstance[0].robot2['Info'] = dictKeyByVal(self.params['info_values'],'redirected')

            else:

                lockerinstance[0].robot2['Info'] = dictKeyByVal(self.params['info_values'],'nop')



    def lasercontrol(self, lockerinstance):

        with lockerinstance[0].lock:

            status = lockerinstance[0].robot2['Status']

            info = lockerinstance[0].robot2['Info']

            est_vg = lockerinstance[0].robot2['Est_VG']

            est_plyty = lockerinstance[0].robot2['Est_PLYTY']

        if self.params['info_values'][info] in ['busy']:
            return

        elif self.params['info_values'][info] in ['nop', 'redirected']:

            if self.params['status_values'][status] in ['nop', 'done']:

                self.redirectlasertoVG(lockerinstance)

            elif self.params['status_values'][status] in ['laser_required']:

                self.redirectlasertoPLYTY(lockerinstance)



    def redirectlasertoPLYTY(self, lockerinstance):

        with lockerinstance[0].lock:

            lockerinstance[0].scout['AutostartOff'] = True

            lockerinstance[0].lcon['InternalControlSet'] = True

            lockerinstance[0].robot2['laserlocked'] = True

            lockerinstance[0].lcon['locklaserloop'] = True

            info = lockerinstance[0].robot2['Info']
        
        if not 'redirected' in self.params['info_values'][info]:

            self.FreezeKdraw()
            
            self.ExControlOff()

    def redirectlasertoVG(self, lockerinstance):

        with lockerinstance[0].lock:

            lockerinstance[0].robot2['laserlocked'] = False

            lockerinstance[0].lcon['locklaserloop'] = False

            info = lockerinstance[0].robot2['Info']

        if 'redirected' in self.params['info_values'][info]:

            self.ResumeKdraw()

