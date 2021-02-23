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
        self.processes = [
            Process(name = 'Window', target = Window, args=(self.lock,)),
            Process(name = 'MyMultiplexer', target = MyMultiplexer, args=(self.lock, self.AmuxConfigurationFile,)),
            Process(name = 'Servo', target = Servo, args=(self.lock, self.ServoConfigurationFile,)),
            Process(name = 'MyLaserControl', target = MyLaserControl, args=(self.lock, self.LconConfigurationFile,)),
            Process(name = 'RobotVG', target = RobotVG, args=(self.lock, self.RobotConfigurationFile, *args,)),
            Process(name = 'PneumaticsVG', target = PneumaticsVG, args=(self.lock, self.PneumaticsConfigurationFile,)),
            Process(name = 'GMOD', target = GMOD, args=(self.lock, self.SICKGMOD0ConfigurationFile,)),
            Process(name = 'Troley', target = Troley, args=(self.lock, self.TroleyConfigurationFile,))
        ]    
        for process in self.processes: 
            process.start()
        self.EventLoop(*args, **kwargs)

    def EventLoop(self, *args, **kwargs):
        while True:
            self.lock[0].lock.acquire()
            console = list(filter(lambda f:f.name == 'Window',self.processes))[0].is_alive()
            if not console:
                self.lock[0].events['closeApplication'] = True
            self.ApplicationAlive = not self.lock[0].events['closeApplication']
            self.lock[0].lock.release()
            if not self.ApplicationAlive:
                self.lock[0].lock.acquire()
                self.lock[0].servo['Alive'] = False
                self.lock[0].mux['Alive'] = False
                self.lock[0].robot['Alive'] = False
                self.lock[0].pistons['Alive'] = False
                self.lock[0].console['Alive'] = False
                self.lock[0].lcon['Alive'] = False
                self.lock[0].lock.release()
                for process in self.processes:
                    print(str(process))
                    process.join()
                break
            self.errorcatching()

    def errorcatching(self):
        for proces in self.processes:
            if not proces.is_alive():
                self.lock[0].lock.acquire()
                self.lock[0].events['closeApplication'] = True
                self.lock[0].lock.release()

if __name__=="__main__":
    freeze_support()
    main = ApplicationManager()
