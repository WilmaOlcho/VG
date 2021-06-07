from Sources.modbusTCPunits import Kawasaki, KawasakiPLYTYParams
from Sources.TactWatchdog import TactWatchdog as WDT
from .common import EventManager, ErrorEventWrite, Bits, dictKeyByVal
from functools import lru_cache
from threading import Thread, currentThread
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
                        lockerinstance[0].robot['Alive'] = self.Alive
                    self.Robotloop(lockerinstance)
                finally:
                    with lockerinstance[0].lock:
                        self.Alive = lockerinstance[0].robot2['Alive']
                        closeapp = lockerinstance[0].events['closeApplication']
                    if closeapp: break


    def Robotloop(self, lockerinstance):
        while self.Alive:
            with lockerinstance[0].lock:
                self.Alive = lockerinstance[0].robot2['Alive']
            if not self.Alive: break
            self.StatusUpdate(lockerinstance)
            self.InfoUpdate(lockerinstance)
            self.lasercontrol(lockerinstance)


    def StatusUpdate(self, lockerinstance):
        try:
            currentstatus = self.read_holding_registers(lockerinstance, registerToStartFrom='status')
            est_plyty = self.read_holding_registers(lockerinstance, registerToStartFrom='est_time_PLYTY')
        except:
            pass
        with lockerinstance[0].lock:
            lockerinstance[0].robot2['Status'] = currentstatus
            lockerinstance[0].robot2['Est_PLYTY'] = est_plyty
            info = lockerinstance[0].robot2['Info']
            est_vg = lockerinstance[0].robot2['Est_VG']
        try:
            self.write_register(lockerinstance, register = 'info', value = info)
            self.write_register(lockerinstance, register = 'est_time_VG', value = est_vg)
        except:
            pass


    def InfoUpdate(self, lockerinstance):
        with lockerinstance[0].lock():
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
            if self.params['status_values'][status] in ['nop']['done']:
                self.redirectlasertoVG(lockerinstance)
            elif self.params['status_values'][status] in ['laser_required']:
                self.redirectlasertoPLYTY(lockerinstance)
            

    def redirectlasertoPLYTY(self, lockerinstance):
        with lockerinstance[0].lock():
            lockerinstance[0].scout['AutostartOff'] = True
            lockerinstance[0].lcon['InternalControlSet'] = True
            lockerinstance[0].robot2['laserlocked'] = True
            lockerinstance[0].lcon['locklaserloop'] = True

    def redirectlasertoVG(self, lockerinstance):
        with lockerinstance[0].lock():
            lockerinstance[0].robot2['laserlocked'] = False
            lockerinstance[0].lcon['locklaserloop'] = False
