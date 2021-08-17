from multiprocessing import Process, current_process, freeze_support, set_start_method
from pathlib import Path
import os, psutil, wmi, re



#Pliki programu, moduły
from Sources.StaticLock import SharedLocker
from Sources.analogmultiplexer import MyMultiplexer, MyLaserControl
from Sources.Kawasaki import RobotVG
from Sources.LaserBeamRedirector import RobotPlyty
from Sources.Pneumatics import PneumaticsVG
from Sources.Servo import Servo
from Sources.Troley import Troley
from Sources.sickgmod import GMOD
#from gui import console
from Sources.UI.MainWindow import Window
from Sources.scout import SCOUT
from Sources.programController import programController as Program




import logging
_logger = logging.getLogger(__name__)


class ApplicationManager(object):
    def __init__(self, *args, **kwargs):
        """
        Application manager initialise StaticLock

        """
        super().__init__(*args, **kwargs)
        __file__ = ''
        
        path = str(Path(__file__).parent.absolute())+'\\'
        lockerinstance = {}
        lockerinstance[0] = SharedLocker(mainpath = path)

        self.processes = []
        with lockerinstance[0].lock:
            for processclass in lockerinstance[0].shared['main'].keys():
                if lockerinstance[0].shared['main'][processclass]:
                    self.processes.append(Process(name = processclass, target = eval(processclass), args=(lockerinstance, *lockerinstance[0].shared['paramfiles'][processclass])) )

        for process in self.processes:
            process.start()
        for process in self.processes:
            with lockerinstance[0].lock:
                lockerinstance[0].shared['PID'][process.name] = process.pid
            print(process.name, process.pid)
        self.EventLoop(lockerinstance, *args, **kwargs)


    def EventLoop(self, lockerinstance, *args, **kwargs):
        ps = []
        psb = []
        sstr = ''
        while True:
            with lockerinstance[0].lock:
                self.ApplicationAlive = not lockerinstance[0].events['closeApplication']
                if not self.ApplicationAlive:
                    for key in lockerinstance[0].shared.keys():
                        if hasattr(lockerinstance[0].shared[key],'__dict__'):
                            cdict = lockerinstance[0].shared[key]
                            if 'Alive' in cdict.keys():
                                cdict['Alive'] = False
            if not self.ApplicationAlive:
                stillalive = False
                for i, process in enumerate(self.processes):
                    pname = str(process.name)
                    if pname not in ps:
                        ps.append(pname)
                        psb.append(False)
                    if process.is_alive():
                        stillalive = True
                        psb[i] = True
                    else:
                        psb[i] = False
                nstr = str(list(zip(ps, psb))) + "App is still alive" if stillalive else "Done"                        
                if not sstr == nstr:
                    print(nstr)
                    sstr = nstr
                if not stillalive: break
            self.errorcatching(lockerinstance)


    def errorcatching(self, lockerinstance):
        restoring = []
        for process in [*self.processes,*restoring]:
            if not process.is_alive():
                with lockerinstance[0].lock:
                   restore = not lockerinstance[0].events['closeApplication']
                if restore:
                    if hasattr(process,"name"):
                        restoring.append(process.name)
                        self.processes.remove(process)
                        if process.name in ['scout','RobotPlyty']:
                            applist = wmi.WMI()
                            def IsProcessValid(process, KnownProcessValue='K-Draw', VariableName='Name'):
                                if hasattr(process, 'Properties_'):
                                    return re.findall(str(KnownProcessValue), str(process.Properties_(VariableName).Value))
                            InstanceWeLookingFor = list(filter(IsProcessValid,self.processes))
                            if InstanceWeLookingFor:
                                psutil.Process(InstanceWeLookingFor[0].ProcessId).terminate()
        for processclass in lockerinstance[0].shared['main'].keys():
            if processclass in restoring:
                process = Process(name = processclass, target = eval(processclass), args=(lockerinstance, *lockerinstance[0].shared['paramfiles'][processclass]))
                self.processes.append(process)
                process.start()
                with lockerinstance[0].lock:
                    lockerinstance[0].shared['PID'][process.name] = process.pid
                print(process.name, 'restored    PID:',process.pid)
        with lockerinstance[0].lock:
            if lockerinstance[0].events['ack']:
                lockerinstance[0].events['Error'] = False
                lockerinstance[0].events['erroracknowledge'] = True
                lockerinstance[0].shared['Errors'] = ''
                for i in range(256):
                    lockerinstance[0].errorlevel[i] = False
                lockerinstance[0].events['ack'] = False
                

#punkt początkowy programu
if __name__=="__main__":
    freeze_support()
    main = ApplicationManager()
