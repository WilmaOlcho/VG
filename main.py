from multiprocessing import Process, Manager, Lock
from Sources.Estun import MyEstun
from Sources.StaticLock import SharedLocker
from Sources.analogmultiplexer import MyMultiplexer
from Sources.Kawasaki import RobotVG
from Sources.Pneumatics import PneumaticsVG

class ApplicationManager(SharedLocker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ServoConfigurationFile = 'servo.ini'
        self.AmuxConfigurationFile = 'multiplexer.ini'
        self.RobotConfigurationFile = 'robot.ini'
        self.PneumaticsConfigurationFile = 'PistonsExample.xml'
        self.processes = [
            Process(target = MyEstun, args=(self.ServoConfigurationFile,*args,)),
            Process(target = MyMultiplexer, args=(self.AmuxConfigurationFile, *args,)),
            Process(target = RobotVG, args=(self.RobotConfigurationFile, *args,)),
            Process(target = PneumaticsVG, args=(self.PneumaticsConfigurationFile, *args,))

        ]
        for process in self.processes: process.start()
        for process in self.processes: process.join()
        self.EventLoop(*args, **kwargs)

    def EventLoop(self, *args, **kwargs):
        while True:
            self.lock.acquire()
            self.ApplicationAlive = not self.events['closeApplication']
            self.lock.release()
            if not self.ApplicationAlive:
                self.lock.acquire()
                self.estun['Alive'] = False
                self.mux['Alive'] = False
                self.robot['Alive'] = False
                self.pistons['Alive'] = False
                self.lock.release()
                break
            self.errorcatching()

    def errorcatching(self):
        self.lock.acquire()
        erroroccured = self.events['Error']
        self.lock.release()
        if erroroccured:
            self.lock.acquire()
            print(self.shared['Errors'])
            for i, err in enumerate(self.errorlevel):
                if err:
                    print("errlvl: " + str(i))
                    self.errorlevel[i] = False
            self.shared['Errors'] = ''
            self.lock.release()
        self.lock.acquire()
        for err in self.errorlevel:
            if err: self.events['Error'] = True
            break
        self.lock.release()

if __name__=="__main__":
    ApplicationManager()
        
        
