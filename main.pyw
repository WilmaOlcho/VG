from multiprocessing import Process, current_process, freeze_support, set_start_method
from Sources.Estun import MyEstun
from Sources.StaticLock import SharedLocker
from Sources.analogmultiplexer import MyMultiplexer, MyLaserControl
from Sources.Kawasaki import RobotVG
from Sources.Pneumatics import PneumaticsVG
from gui import console
from pathlib import Path

class ApplicationManager(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locker = SharedLocker()
        self.lock = {0:self.locker}
        path = str(Path(__file__).parent.absolute())+'\\'
        self.ServoConfigurationFile = path + 'servoEstun.ini'
        self.AmuxConfigurationFile = path + 'amuxConfiguration.json'
        self.LconConfigurationFile = path + 'amuxConfiguration.json'
        self.RobotConfigurationFile = path + 'robotConfiguration.json'
        self.PneumaticsConfigurationFile = path + 'PneumaticsConfiguration.json'
        self.processes = [
            Process(name = 'console', target = console, args=(self.lock,)),
            Process(name = 'MyEstun', target = MyEstun, args=(self.lock, self.ServoConfigurationFile,)),
            Process(name = 'MyMultiplexer', target = MyMultiplexer, args=(self.lock, self.AmuxConfigurationFile,)),
            Process(name = 'MyLaserControl', target = MyLaserControl, args=(self.lock, self.LconConfigurationFile,)),
            Process(name = 'RobotVG', target = RobotVG, args=(self.lock, self.RobotConfigurationFile, *args,)),
            Process(name = 'PneumaticsVG', target = PneumaticsVG, args=(self.lock, self.PneumaticsConfigurationFile,))
        ]   
        for process in self.processes: 
            process.start()
        self.EventLoop(*args, **kwargs)

    def EventLoop(self, *args, **kwargs):
        while True:
            self.lock[0].lock.acquire()
            console = list(filter(lambda f:f.name == 'console',self.processes))[0].is_alive()
            if not console:
                self.lock[0].events['closeApplication'] = True
            self.ApplicationAlive = not self.lock[0].events['closeApplication']
            self.lock[0].lock.release()
            if not self.ApplicationAlive:
                self.lock[0].lock.acquire()
                self.lock[0].estun['Alive'] = False
                self.lock[0].mux['Alive'] = False
                self.lock[0].robot['Alive'] = False
                self.lock[0].pistons['Alive'] = False
                self.lock[0].console['Alive'] = False
                self.lock[0].lcon['Alive'] = False
                self.lock[0].lock.release()
                for process in self.processes: 
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
