import time
from threading import Thread
from multiprocessing import Process, Manager, Lock

def BlankFunc(*args, **kwargs):
    pass

class TactWatchdog():
    scaleMultiplier = {
        'ns':1,
        'us':1000,
        'ms':1000000,
        's':1000000000,
        'm':60000000000,
        'h':3600000000000,
        'd':86400000000000,         ##Just for fun
        'w':604800000000000,        #
        'mth':18144000000000000,    #
        'y':217728000000000000}     #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timePoint = 0
        self.setpoint()

    def setpoint(self):
        self.timePoint = time.time_ns()

    def elapsed(self):
        return time.time_ns() - self.timePoint

    def WDTloop(self, shared, lock, limitval,
                errToRaise = '/n',
                caption = 'WDTTimer',
                scale = 'ns',
                errorlevel = 255,
                eventToCatch = 'ack',
                additionalFuncOnStart = BlankFunc,
                additionalFuncOnLoop = BlankFunc,
                additionalFuncOnCatch = BlankFunc,
                additionalFuncOnExceed = BlankFunc,
                *args, **kwargs):
        additionalFuncOnStart(shared, lock, *args, **kwargs)
        self.setpoint()
        limitval *= self.scaleMultiplier[scale]
        while True:
            additionalFuncOnLoop(shared, lock, *args, **kwargs)
            lock.acquire()
            shared['TactWDT'] |= True
            if eventToCatch[0] == '-':
                event = not(shared['Events'][eventToCatch[1:]])
            else:
                event = shared['Events'][eventToCatch]
            lock.release()
            if event:
                additionalFuncOnCatch(shared, lock, *args, **kwargs)
                break
            if self.elapsed() >= limitval:
                lock.acquire()
                shared['Errors'] += errToRaise
                shared['Error'][errorlevel] = True
                lock.release()
                additionalFuncOnExceed(shared, lock, *args, **kwargs)
                break

    @classmethod
    def WDT(cls, shared, lock,
                limitval = 100,
                errToRaise = 'limit',
                caption = 'Event',
                scale = 'ms',
                errorlevel = 255,
                eventToCatch = 'ack',
                additionalFuncOnStart = BlankFunc,
                additionalFuncOnLoop = BlankFunc,
                additionalFuncOnCatch = BlankFunc,
                additionalFuncOnExceed = BlankFunc):
        WDT = cls()
        thread = Thread(target=WDT.WDTloop, args = (shared, lock, limitval,
                                                    errToRaise,
                                                    caption, scale, errorlevel,
                                                    eventToCatch,
                                                    additionalFuncOnStart,
                                                    additionalFuncOnLoop,
                                                    additionalFuncOnCatch,
                                                    additionalFuncOnExceed), daemon = False)
        thread.start()

def lockDecorator(func):
    def Internal(shared, lock, *args, **kwargs):
        lock.acquire()
        func(shared, lock, *args, **kwargs)
        lock.release()
    return Internal
    
if __name__=='__main__': ##Test
    shared = {
        'Events':{
            'ff':True,
            'ack':False},
        'TactWDT':False,
        'Errors':'',
        'Error':256*[False]
    }
    lock = Lock()
    @lockDecorator
    def decproc(shared, lock, *args, **kwargs):
        shared['Events']['ff'] = False
        print("Zuparomana")
    @lockDecorator
    def decproc2(shared, lock, *args, **kwargs):
        shared['Events']['ack'] = True
        print("Giuseppe")
    TactWatchdog.WDT(shared, lock, errToRaise = 'doopa', limitval = 3)
    TactWatchdog.WDT(shared, lock, caption = 'doopa2', limitval = 8)
    TactWatchdog.WDT(shared, lock, errToRaise = 'Servo', limitval = 10000, scale = 'ms', errorlevel = 3)
    TactWatchdog.WDT(shared, lock, caption = 'ESTUN leci w trabke', limitval = 20, scale = 's',eventToCatch = '-ff', additionalFuncOnCatch = decproc2)
    TactWatchdog.WDT(shared, lock, errToRaise = 'sd', limitval = 10, scale = 's')
    TactWatchdog.WDT(shared, lock, limitval = 4, scale = 's')
    TactWatchdog.WDT(shared, lock, errToRaise = 'gebo', limitval = 4, scale = 's', additionalFuncOnExceed = decproc)
    dt = True
    last = ''
    while dt:
        lock.acquire()
        dt = shared['TactWDT']
        shared['TactWDT'] = False
        news = shared['Errors']
        if last != news:
            print(news.replace(last,'',1))
            last = shared['Errors']
        lock.release()
    for i in range(len(shared['Error'])):
        if shared['Error'][i] == True:
            print("Error " + str(i))