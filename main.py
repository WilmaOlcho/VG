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
        for i in range(len(self.processes)):
            self.processes[i].start()
        for i in range(len(self.processes)):
            self.processes[i].join()
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

if __name__=="__main__":
    ApplicationManager()
        
        
