from multiprocessing import Process, current_process, freeze_support, set_start_method

#import site # py2exe can't find it
#import os, re
#for path in os.environ['PATH'].split(';'):
#    if any(re.findall('Python',path)):
#        if not re.findall('Scripts',path) and not re.findall('site-packgages',path):
#            site.addsitedir(path+'lib\\site-packages')
#        else:
#            site.addsitedir(path)

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
from pathlib import Path
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
        self.EventLoop(self.lock, *args, **kwargs)

    def EventLoop(self, lockerinstance, *args, **kwargs):
        ps = []
        psb = []
        sstr = ''
        while True:
            with self.lock[0].lock:
                self.ApplicationAlive = not self.lock[0].events['closeApplication']
                if not self.ApplicationAlive:
                    self.lock[0].servo['Alive'] = False
                    self.lock[0].mux['Alive'] = False
                    self.lock[0].robot['Alive'] = False
                    self.lock[0].pistons['Alive'] = False
                    self.lock[0].console['Alive'] = False
                    self.lock[0].lcon['Alive'] = False
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
        for proces in self.processes:
            if not proces.is_alive():
                with self.lock[0].lock:
                    self.lock[0].events['closeApplication'] = True
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
