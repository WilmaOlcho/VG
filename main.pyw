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
from Sources.Pneumatics import PneumaticsVG
from Sources.Servo import Servo
from Sources.Troley import Troley
from Sources.sickgmod import GMOD
#from gui import console
from Sources.UI.MainWindow import Window
from pathlib import Path
from Sources.scout import SCOUT
from Sources.programController import programController

class ApplicationManager(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        __file__ = ''
        self.locker = SharedLocker()
        self.lock = {0:self.locker}
        path = str(Path(__file__).parent.absolute())+'\\'
        self.AmuxConfigurationFile = path + 'amuxConfiguration.json'
        self.LconConfigurationFile = path + 'amuxConfiguration.json'
        self.RobotConfigurationFile = path + 'robotConfiguration.json'
        self.ServoConfigurationFile = path + 'ServoSettings.json'
        self.TroleyConfigurationFile = path + 'Troleysettings.json'
        self.PneumaticsConfigurationFile = path + 'PneumaticsConfiguration.json'
        self.SICKGMOD0ConfigurationFile = path + 'SICKGMODconfiguration.json'
        self.ScoutConfigurationFile = path + 'Scoutconfiguration.json'
        self.programs = path + 'Programs.json'
        self.widgets = path + 'widgetsettings.json'
        self.processes = [
            Process(name = 'Window', target = Window, args=(self.lock,self.widgets, self.programs)),
            Process(name = 'MyMultiplexer', target = MyMultiplexer, args=(self.lock, self.AmuxConfigurationFile,)),
            Process(name = 'Servo', target = Servo,  args=(self.lock, self.ServoConfigurationFile,)),
            Process(name = 'MyLaserControl', target = MyLaserControl, args=(self.lock, self.LconConfigurationFile,)),
            Process(name = 'RobotVG', target = RobotVG,  args=(self.lock, self.RobotConfigurationFile, *args,)),
            Process(name = 'PneumaticsVG', target = PneumaticsVG, args=(self.lock, self.PneumaticsConfigurationFile,)),
            Process(name = 'GMOD', target = GMOD, args=(self.lock, self.SICKGMOD0ConfigurationFile,)),
            Process(name = 'Troley', target = Troley, args=(self.lock, self.TroleyConfigurationFile,)),
            Process(name = 'Program', target = programController, args=(self.lock, self.programs,)),
            Process(name = 'SCOUT', target = SCOUT, args = (self.lock, self.ScoutConfigurationFile,))
        ]    
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
                lockerinstance[0]['Errors'] = ''
                for i in range(256):
                    lockerinstance[0].errorlevel[i] = False
                lockerinstance[0].events['ack'] = False
                


if __name__=="__main__":
    freeze_support()
    main = ApplicationManager()
