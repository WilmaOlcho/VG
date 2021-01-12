
if True:

    from multiprocessing import Process, current_process
    from Sources.Estun import MyEstun
    from Sources.StaticLock import SharedLocker
    from Sources.analogmultiplexer import MyMultiplexer, MyLaserControl
    from Sources.Kawasaki import RobotVG
    from Sources.Pneumatics import PneumaticsVG
    from gui import console



    class ApplicationManager(object):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            locker = SharedLocker()
            self.lock = {0:locker}
            path = 'C:/users/operator/documents/python/vg/'
            self.ServoConfigurationFile = path + 'servoEstun.ini'
            self.AmuxConfigurationFile = path + 'amuxConfiguration.json'
            self.LconConfigurationFile = path + 'amuxConfiguration.json'
            self.RobotConfigurationFile = path + 'robotConfiguration.json'
            self.PneumaticsConfigurationFile = path + 'PneumaticsConfiguration.json'
            self.processes = [
                Process(name = 'console', target = console, args=(self.lock,)),
                Process(name = 'MyEstun', target = MyEstun, args=(self.lock, self.ServoConfigurationFile,*args,)),
                Process(name = 'MyMultiplexer', target = MyMultiplexer, args=(self.lock, self.AmuxConfigurationFile, *args,)),
                Process(name = 'MyLaserControl', target = MyLaserControl, args=(self.lock, self.LconConfigurationFile, *args,)),
                Process(name = 'RobotVG', target = RobotVG, args=(self.lock, self.RobotConfigurationFile, *args,)),
                Process(name = 'PneumaticsVG', target = PneumaticsVG, args=(self.lock, self.PneumaticsConfigurationFile, *args,))

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
        
        
