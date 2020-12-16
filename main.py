
if True:

    from multiprocessing import Process
    #from Sources.Estun import MyEstun
    from Sources.StaticLock import SharedLocker
    #from Sources.analogmultiplexer import MyMultiplexer
    from Sources.Kawasaki import RobotVG
    #from Sources.Pneumatics import PneumaticsVG
    from gui import console



    class ApplicationManager(object):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            locker = SharedLocker()
            self.lock = {0:locker}
            self.ServoConfigurationFile = 'servo.ini'
            self.AmuxConfigurationFile = 'multiplexer.ini'
            self.RobotConfigurationFile = 'robot.ini'
            self.PneumaticsConfigurationFile = 'PistonsExample.xml'
            self.processes = [
                Process(target = console, args=(self.lock,) ),
                Process(target = console, args=(self.lock,) )
                #Process(target = MyEstun, args=(self.ServoConfigurationFile,*args,)),
                #Process(target = MyMultiplexer, args=(self.AmuxConfigurationFile, *args,)),
                #Process(target = RobotVG, args=(self.RobotConfigurationFile, *args,)),
                #Process(target = PneumaticsVG, args=(self.PneumaticsConfigurationFile, *args,))

            ]   
            for process in self.processes: process.start()
            for process in self.processes: process.join()
            self.EventLoop(*args, **kwargs)

        def EventLoop(self, *args, **kwargs):
            while True:
                self.lock[0].lock.acquire()
                self.ApplicationAlive = not self.lock[0].events['closeApplication']
                self.lock[0].lock.release()
                if not self.ApplicationAlive:
                    self.lock[0].lock.acquire()
                    self.lock[0].estun['Alive'] = False
                    self.lock[0].mux['Alive'] = False
                    self.lock[0].robot['Alive'] = False
                    self.lock[0].pistons['Alive'] = False
                    self.lock[0].console['Alive'] = False
                    self.lock[0].lock.release()
                    break
                #self.errorcatching()

        def errorcatching(self):
            self.lock[0].lock.acquire()
            erroroccured = self.lock[0].events['Error']
            self.lock[0].lock.release()
            if erroroccured:
                self.lock[0].lock.acquire()
                print(self.lock[0].shared['Errors'])
                for i, err in enumerate(self.lock[0].errorlevel):
                    if err:
                        print("errlvl: " + str(i))
                        self.lock[0].errorlevel[i] = False
                self.lock[0].shared['Errors'] = ''
                self.lock[0].lock.release()
                self.lock[0].lock.acquire()
                for err in self.lock[0].errorlevel:
                    if err: self.lock[0].events['Error'] = True
                    break
                self.lock[0].lock.release()

if __name__=="__main__":
    ApplicationManager()
        
        
