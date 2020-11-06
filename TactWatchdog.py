import time
from threading import Thread
from multiprocessing import Process, Manager, Lock

def BlankFunc():
    pass

class TactWatchdog():
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
                scale = 'ns',
                errorlevel = 0,
                eventToCatch = 'ack',
                additionalfuncOnStart = BlankFunc,
                additionalfuncOnLoop = BlankFunc,
                additionalfuncOnCatch = BlankFunc):
        additionalfuncOnStart()
        self.setpoint()
        if scale == 'ns':
            pass
        elif scale == 'us':
            limitval *= 1000
        elif scale == 'ms':
            limitval *= 1000000
        elif scale == 's':
            limitval *= 1000000000
        while True:
            additionalfuncOnLoop()
            lock.acquire()
            shared['TactWDT'] |= True
            if eventToCatch[0] == '-':
                event = not(shared['Events'][eventToCatch[1:]])
            else:
                event = shared['Events'][eventToCatch]
            lock.release()
            if event:
                break
            if self.elapsed() >= limitval:
                lock.acquire()
                shared['Errors'] += errToRaise
                shared['Error'][errorlevel] = True
                lock.release()
                break
        additionalfuncOnCatch()

    @classmethod
    def limit(cls, shared, lock,
                errToRaise = 'limit',
                limitval = 100,
                scale = 'ms',
                errorlevel=0,
                eventToCatch = 'ack',
                additionalfuncOnStart = BlankFunc,
                additionalfuncOnLoop = BlankFunc,
                additionalfuncOnCatch = BlankFunc):
        WDT = cls()
        thread = Thread(target=WDT.WDTloop, args = (shared, lock, limitval, errToRaise, scale, errorlevel, eventToCatch,additionalfuncOnStart,additionalfuncOnLoop,additionalfuncOnCatch), daemon = False)
        thread.start()
    @classmethod
    def WDT(cls, shared, lock,
                caption = 'Error',
                limitval = 1,
                scale = 's',
                errorlevel=0,
                eventToCatch = 'ack',
                additionalfuncOnStart = BlankFunc,
                additionalfuncOnLoop = BlankFunc,
                additionalfuncOnCatch = BlankFunc):
        WDT = cls()
        thread = Thread(target=WDT.WDTloop, args = (shared, lock, limitval, caption, scale, errorlevel, eventToCatch,additionalfuncOnStart,additionalfuncOnLoop,additionalfuncOnCatch), daemon = False)
        thread.start()



if __name__=='__main__': ##Test
    shared = {
        'Events':{
            'ff':True,
            'ack':False},
        'TactWDT':False,
        'Errors':'',
        'Error':255*[False]
    }
    lock = Lock()
    def decproc():
        lock.acquire()
        shared['Events']['ff'] = False
        lock.release()
    TactWatchdog.limit(shared, lock, errToRaise = 'doopa', limitval = 3)
    TactWatchdog.WDT(shared, lock, caption = 'doopa2', limitval = 8)
    TactWatchdog.limit(shared, lock, limitval = 4, scale = 's')
    TactWatchdog.limit(shared, lock, errToRaise = 'Servo', limitval = 10000, scale = 'ms', errorlevel = 3)
    TactWatchdog.limit(shared, lock, errToRaise = 'sd', limitval = 10, scale = 's')
    TactWatchdog.WDT(shared, lock, caption = 'ESTUN leci w trabke', limitval = 200, scale = 's',eventToCatch = '-ff')
    TactWatchdog.limit(shared, lock, errToRaise = 'gebo', limitval = 4, scale = 's', additionalfuncOnCatch = decproc)
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