import time
import threading as thr
from .common import BlankFunc, writeInLambda, dictKeyByVal, ErrorEventWrite
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
        with lockerinstance[0].lock:
            lockerinstance[0].wdt.append(thr.currentThread().name)
        additionalFuncOnStart()
        self.setpoint()
        limitval *= self.scaleMultiplier[scale]
        self.active = True
        retlock = False
        while True:
            ret = additionalFuncOnLoop()
            with lockerinstance[0].lock:
                lockerinstance[0].shared['TactWDT'] = True
                if eventToCatch[0] == '-':
                    event = not(lockerinstance[0].events[eventToCatch[1:]])
                else:
                    event = lockerinstance[0].events[eventToCatch]
            if event:
                with lockerinstance[0].lock:
                    if eventToCatch[0] == '-':
                        lockerinstance[0].events[eventToCatch[1:]] = True
                    else:
                        lockerinstance[0].events[eventToCatch] = False
                additionalFuncOnCatch()
                break
            if ret != 'scoutlocked':
                if retlock:
                    retlock = False
                    self.setpoint()
                if self.elapsed() >= limitval:
                    if not noerror: ErrorEventWrite(lockerinstance, errstring = errToRaise, errorlevel = errorlevel)
                    additionalFuncOnExceed()
                    self.Destruct()
                    break
            elif not retlock:
                retlock = True
                limitval = limitval - self.elapsed()
            with lockerinstance[0].lock:
                Alive = thr.currentThread().name in lockerinstance[0].wdt and not lockerinstance[0].events['closeApplication']
            if self.destruct or not Alive:
                break
        self.active = False
        with lockerinstance[0].lock:
            if thr.currentThread().name in lockerinstance[0].wdt:
                lockerinstance[0].wdt.remove(thr.currentThread().name)

    @classmethod
    def WDT(cli,
            lockerinstance,
            limitval = 100,
            errToRaise = '',
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
        if 'timeout' in kwargs.keys(): limitval = kwargs.pop('timeout')
        #if not errToRaise:
        #    with lockerinstance[0].lock:
        #        i = 0
        #        while True:
        #            if not "WDT: "+str(i) in lockerinstance[0].wdt:
        #                break
        #            else:
        #                i +=1
        #    errToRaise = str(i)
        with lockerinstance[0].lock:
            timerActive = 'WDT: '+errToRaise in lockerinstance[0].wdt
        if not timerActive:
            timer = thr.Thread(target=cli().WDTloop, args = (lockerinstance,
                                                    limitval,
                                                    errToRaise,
                                                    caption, scale, errorlevel,
                                                    eventToCatch,
                                                    additionalFuncOnStart,
                                                    additionalFuncOnLoop,
                                                    additionalFuncOnCatch,
                                                    additionalFuncOnExceed,
                                                    noerror,
                                                    *args), daemon = True)
            timer.setName('WDT: ' + errToRaise)
            timer.start()
            return timer.name

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
        with locker[0].lock:
            locker[0].events['RobotMoving'] = False
    TactWatchdog.WDT(locker, errToRaise = 'ERR3', limitval = 5, scale = 's', additionalFuncOnExceed = Foo2)
    dt = True
    last = ''
    while dt:
        with locker[0].lock:
            dt = locker[0].shared['TactWDT']
            locker[0].shared['TactWDT'] = False
            news = locker[0].shared['Errors']
            if last != news:
                print(news.replace(last,'',1))
                last = locker[0].shared['Errors']
    with locker[0].lock:
        print(dictKeyByVal(locker[0].errorlevel,True))
    