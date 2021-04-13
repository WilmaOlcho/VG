from multiprocessing import Process, current_process, freeze_support, set_start_method
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
        self.processes = [
            Process(name = 'Window', target = Window, daemon=True, args=(self.lock,"")),
            Process(name = 'MyMultiplexer', target = MyMultiplexer, daemon=True, args=(self.lock, self.AmuxConfigurationFile,)),
            Process(name = 'Servo', target = Servo, daemon=True, args=(self.lock, self.ServoConfigurationFile,)),
            Process(name = 'MyLaserControl', target = MyLaserControl, daemon=True, args=(self.lock, self.LconConfigurationFile,)),
            Process(name = 'RobotVG', target = RobotVG, daemon=True, args=(self.lock, self.RobotConfigurationFile, *args,)),
            Process(name = 'PneumaticsVG', target = PneumaticsVG, daemon=True, args=(self.lock, self.PneumaticsConfigurationFile,)),
            Process(name = 'GMOD', target = GMOD, daemon=True, args=(self.lock, self.SICKGMOD0ConfigurationFile,)),
            Process(name = 'Troley', target = Troley, daemon=True, args=(self.lock, self.TroleyConfigurationFile,)),
            Process(name = 'Program', target = programController, daemon=True, args=(self.lock, self.programs,)),
            Process(name = 'SCOUT', target = SCOUT, daemon=True, args = (self.lock, self.ScoutConfigurationFile,))
        ]    
        for process in self.processes: 
            process.start()
        self.EventLoop(*args, **kwargs)

    def EventLoop(self, *args, **kwargs):
        ps = []
        psb = []
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
                        
                print(str(list(zip(ps, psb))), "App is still alive" if stillalive else "Done")
                if not stillalive: break
            self.errorcatching()

    def errorcatching(self):
        for proces in self.processes:
            if not proces.is_alive():
                with self.lock[0].lock:
                    self.lock[0].events['closeApplication'] = True

if __name__=="__main__":
    freeze_support()
    main = ApplicationManager()
