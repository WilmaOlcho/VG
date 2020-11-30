from multiprocessing import Process, Manager, Lock
from Sources.Estun import MyEstun
from Sources.StaticLock import SharedLocker

class ApplicationManager(SharedLocker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processes = [
            Process(target = MyEstun.Run, args=(*args,))
        ]
        for i in range(len(self.processes)):
            self.processes[i].start()
        for i in range(len(self.processes)):
            self.processes[i].join()


if __name__=="__main__":
    ApplicationManager()
        
        
