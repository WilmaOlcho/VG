from multiprocessing import Process, current_process, freeze_support, set_start_method
from pathlib import Path
import os

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
        super().__init__(*args, **kwargs)
        __file__ = ''
        
        path = str(Path(__file__).parent.absolute())+'\\'
        self.locker = SharedLocker(mainpath = path)
        self.lock = {0:self.locker}

        self.processes = []
        with self.locker.lock:
            for processclass in self.locker.shared['main'].keys():
                if self.locker.shared['main'][processclass]:
                    self.processes.append(Process(name = processclass, target = eval(processclass), args=(self.lock, *self.locker.shared['paramfiles'][processclass])) )

        for process in self.processes:
            process.start()
        for process in self.processes:
            with self.locker.lock:
                self.locker.shared['PID'][process.name] = process.pid
            print(process.name, process.pid)
        self.EventLoop(self.lock, *args, **kwargs)


    def EventLoop(self, lockerinstance, *args, **kwargs):
        ps = []
        psb = []
        sstr = ''
        while True:
            with self.lock[0].lock:
                self.ApplicationAlive = not self.lock[0].events['closeApplication']
                if not self.ApplicationAlive:
                    for key in self.lock[0].shared.keys():
                        if hasattr(self.lock[0].shared[key],'__dict__'):
                            cdict = self.lock[0].shared[key]
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
                with self.lock[0].lock:
                   restore = not self.lock[0].events['closeApplication']
                if restore:
                    if hasattr(process,"name"):
                        restoring.append(process.name)
                        self.processes.remove(process)
        for processclass in self.locker.shared['main'].keys():
            if processclass in restoring:
                process = Process(name = processclass, target = eval(processclass), args=(self.lock, *self.locker.shared['paramfiles'][processclass]))
                self.processes.append(process)
                process.start()
                with lockerinstance[0].lock:
                    self.lock[0].shared['PID'][process.name] = process.pid
                print(process.name, 'restored    PID:',process.pid)
        with lockerinstance[0].lock:
            if lockerinstance[0].events['ack']:
                lockerinstance[0].events['Error'] = False
                lockerinstance[0].events['erroracknowledge'] = True
                lockerinstance[0].shared['Errors'] = ''
                for i in range(256):
                    lockerinstance[0].errorlevel[i] = False
                lockerinstance[0].events['ack'] = False
                


if __name__=="__main__":
    freeze_support()
    main = ApplicationManager()
