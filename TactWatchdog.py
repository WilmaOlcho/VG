import time
from threading import Thread
from multiprocessing import Process, Manager, Lock

class TactWatchdog():
    timePoint = 0
    def __init__(self, *args, **kwargs):
        self.setpoint()

    def setpoint(self):
        self.timePoint = time.time_ns()

    def elapsed(self):
        return time.time_ns() - self.timePoint

    def WDTloop(self, shared, lock, limitval, errToRaise = '/n', scale = 'ns', errorlevel = 0, eventToCatch = 'ack'):
        self.setpoint()
        if scale == 'ns':
            pass
        if scale == 'us':
            limitval *= 1000
        if scale == 'ms':
            limitval *= 1000000
        if scale == 's':
            limitval *= 1000000000
        while True:
            lock.acquire()
            shared['TactWDT'] |= True
            event = shared['Events'][eventToCatch]
            lock.release()
            if event == True:
                #lock.acquire()
                #shared['Errors'] += "\nEVENT HAPPENED"
                #lock.release()
                break
            if self.elapsed() >= limitval:
                lock.acquire()
                shared['Errors'] += errToRaise
                shared['Error'][errorlevel] = True
                lock.release()
                break

    @classmethod
    def limit(cls, shared, lock, errToRaise = 'limit', limitval = 100, scale = 'ms', errorlevel=0, eventToCatch = 'ack'):
        WDT = cls()
        thread = Thread(target=WDT.WDTloop, args = (shared, lock, limitval, errToRaise, scale, errorlevel, eventToCatch), daemon = False)
        thread.start()
    @classmethod
    def WDT(cls, shared, lock, caption = 'Error', limitval = 1, scale = 's', errorlevel=0, eventToCatch = 'ack'):
        WDT = cls()
        thread = Thread(target=WDT.WDTloop, args = (shared, lock, limitval, caption, scale, errorlevel, eventToCatch), daemon = False)
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
    TactWatchdog.limit(shared, lock, errToRaise = 'doopa', limitval = 3)
    TactWatchdog.WDT(shared, lock, caption = 'doopa2', limitval = 8)
    TactWatchdog.limit(shared, lock, limitval = 4, scale = 's')
    TactWatchdog.limit(shared, lock, errToRaise = 'Servo', limitval = 10000, scale = 'ms', errorlevel = 3)
    TactWatchdog.limit(shared, lock, errToRaise = 'sd', limitval = 10, scale = 's')
    TactWatchdog.WDT(shared, lock, caption = 'ESTUN leci w trabke', limitval = 5, scale = 's',eventToCatch = 'ff')
    TactWatchdog.limit(shared, lock, errToRaise = 'gebo', limitval = 4, scale = 's')
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