import time
from threading import Thread
from Sources.misc import BlankFunc, writeInLambda, dictKeyByVal
from Sources.StaticLock import SharedLocker

class TactWatchdog(object):
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
        self.destruct = False
        self.active = False

    def Destruct(self):
        self.destruct = True

    def setpoint(self):
        self.timePoint = time.time_ns()

    def elapsed(self):
        return time.time_ns() - self.timePoint

    def WDTloop(self,lockerinstance,
                limitval=0,
                errToRaise = '/n',
                caption = 'WDTTimer',
                scale = 'ns',
                errorlevel = 255,
                eventToCatch = 'ack',
                additionalFuncOnStart = BlankFunc,
                additionalFuncOnLoop = BlankFunc,
                additionalFuncOnCatch = BlankFunc,
                additionalFuncOnExceed = BlankFunc,
                noerror = False,
                *args, **kwargs):
        additionalFuncOnStart()
        self.setpoint()
        limitval *= self.scaleMultiplier[scale]
        self.active = True
        while True:
            additionalFuncOnLoop()
            lockerinstance[0].lock.acquire()
            lockerinstance[0].shared['TactWDT'] = True
            if eventToCatch[0] == '-':
                event = not(lockerinstance[0].events[eventToCatch[1:]])
            else:
                event = lockerinstance[0].events[eventToCatch]
            lockerinstance[0].lock.release()
            if event:
                additionalFuncOnCatch()
                break
            if self.elapsed() >= limitval:
                if not noerror:
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].shared['Errors'] += errToRaise
                    lockerinstance[0].errorlevel[errorlevel] = True
                    lockerinstance[0].lock.release()
                additionalFuncOnExceed()
                self.Destruct()
                break
            if self.destruct:
                break
        self.active = False

    @classmethod
    def WDT(cli,
            lockerinstance,
            limitval = 100,
            errToRaise = 'limit',
            caption = 'Event',
            scale = 'ms',
            errorlevel = 255,
            eventToCatch = 'ack',
            additionalFuncOnStart = BlankFunc,
            additionalFuncOnLoop = BlankFunc,
            additionalFuncOnCatch = BlankFunc,
            additionalFuncOnExceed = BlankFunc,
            noerror = False,
            *args, **kwargs):
        WDT = cli()
        thread = Thread(target=WDT.WDTloop, args = (lockerinstance,
                                                    limitval,
                                                    errToRaise,
                                                    caption, scale, errorlevel,
                                                    eventToCatch,
                                                    additionalFuncOnStart,
                                                    additionalFuncOnLoop,
                                                    additionalFuncOnCatch,
                                                    additionalFuncOnExceed,
                                                    noerror,
                                                    *args), daemon = False)
        thread.start()

if __name__=='__main__': ##Test
    lockerbaseinstance = SharedLocker()
    locker = {0:lockerbaseinstance}
    TactWatchdog.WDT(locker, errToRaise = 'ERR1', limitval = 3)
    TactWatchdog.WDT(locker, caption = 'TACT1EXCEEDED', limitval = 8)
    TactWatchdog.WDT(locker, errToRaise = 'Servo', limitval = 10000, scale = 'ms', errorlevel = 3)
    def Foo1():
        TactWatchdog.WDT(locker, limitval=1, errToRaise='CATCH', scale='ms', errorlevel=15)
    TactWatchdog.WDT(locker, errToRaise = 'Duuupa', caption = 'ESTUN working', limitval = 30, scale = 's',eventToCatch = '-RobotMoving', additionalFuncOnCatch = Foo1)
    TactWatchdog.WDT(locker, errToRaise = 'ERR2', limitval = 10, scale = 's')
    TactWatchdog.WDT(locker, limitval = 4, scale = 's')
    def Foo2():
        locker[0].lock.acquire()
        locker[0].events['RobotMoving'] = False
        locker[0].lock.release()
    TactWatchdog.WDT(locker, errToRaise = 'ERR3', limitval = 5, scale = 's', additionalFuncOnExceed = Foo2)
    dt = True
    last = ''
    while dt:
        locker[0].lock.acquire()
        dt = locker[0].shared['TactWDT']
        locker[0].shared['TactWDT'] = False
        news = locker[0].shared['Errors']
        if last != news:
            print(news.replace(last,'',1))
            last = locker[0].shared['Errors']
        locker[0].lock.release()
    locker[0].lock.acquire()
    print(dictKeyByVal(locker[0].errorlevel,True))
    locker[0].lock.release()

    