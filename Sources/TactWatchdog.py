import time
from threading import Thread
from misc import BlankFunc, writeInLambda, dictKeyByVal
from StaticLock import SharedLocker

class TactWatchdog(SharedLocker):
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

    def Destruct(self):
        self.destruct = True

    def setpoint(self):
        self.timePoint = time.time_ns()

    def elapsed(self):
        return time.time_ns() - self.timePoint

    def WDTloop(self, limitval,
                errToRaise = '/n',
                caption = 'WDTTimer',
                scale = 'ns',
                errorlevel = 255,
                eventToCatch = 'ack',
                additionalFuncOnStart = None,
                additionalFuncOnLoop = None,
                additionalFuncOnCatch = None,
                additionalFuncOnExceed = None,
                *args, **kwargs):
        if additionalFuncOnStart is not None:
            eval(additionalFuncOnStart)
        self.setpoint()
        print(limitval)
        limitval *= self.scaleMultiplier[scale]
        while True:
            if additionalFuncOnLoop is not None:
                eval(additionalFuncOnLoop)
            self.lock.acquire()
            self.shared['TactWDT'] |= True
            if eventToCatch[0] == '-':
                event = not(self.events[eventToCatch[1:]])
            else:
                event = self.events[eventToCatch]
            self.lock.release()
            if event:
                if additionalFuncOnCatch is not None:
                    eval(additionalFuncOnCatch)
                break
            if self.elapsed() >= limitval:
                self.lock.acquire()
                self.shared['Errors'] += errToRaise
                self.errorlevel[errorlevel] = True
                self.lock.release()
                if additionalFuncOnExceed is not None:
                    eval(additionalFuncOnExceed)
                self.Destruct()
                break
            if self.destruct:
                break

    @classmethod
    def WDT(cli,
            limitval = 100,
            errToRaise = 'limit',
            caption = 'Event',
            scale = 'ms',
            errorlevel = 255,
            eventToCatch = 'ack',
            additionalFuncOnStart = None,
            additionalFuncOnLoop = None,
            additionalFuncOnCatch = None,
            additionalFuncOnExceed = None,
            *args, **kwargs):
        WDT = cli()
        thread = Thread(target=WDT.WDTloop, args = (limitval,
                                                    errToRaise,
                                                    caption, scale, errorlevel,
                                                    eventToCatch,
                                                    additionalFuncOnStart,
                                                    additionalFuncOnLoop,
                                                    additionalFuncOnCatch,
                                                    additionalFuncOnExceed,
                                                    *args), daemon = False)
        thread.start()

if __name__=='__main__': ##Test
    SharedLocker()
    TactWatchdog.WDT(errToRaise = 'ERR1', limitval = 3)
    TactWatchdog.WDT(caption = 'TACT1EXCEEDED', limitval = 8)
    TactWatchdog.WDT(errToRaise = 'Servo', limitval = 10000, scale = 'ms', errorlevel = 3)
    TactWatchdog.WDT(errToRaise = 'Duuupa', caption = 'ESTUN working', limitval = 30, scale = 's',eventToCatch = '-RobotMoving', additionalFuncOnCatch = "TactWatchdog.WDT(limitval=1, errToRaise='CATCH', scale='ms', errorlevel=15)")
    TactWatchdog.WDT(errToRaise = 'ERR2', limitval = 10, scale = 's')
    TactWatchdog.WDT(limitval = 4, scale = 's')
    TactWatchdog.WDT(errToRaise = 'ERR3', limitval = 5, scale = 's', additionalFuncOnExceed = "SharedLocker.WithLock(function = writeInLambda, SharedLocker.events['RobotMoving'], False)")
    dt = True
    last = ''
    while dt:
        SharedLocker.lock.acquire()
        dt = SharedLocker.shared['TactWDT']
        SharedLocker.shared['TactWDT'] = False
        news = SharedLocker.shared['Errors']
        if last != news:
            print(news.replace(last,'',1))
            last = SharedLocker.shared['Errors']
        SharedLocker.lock.release()
    SharedLocker.lock.acquire()
    print(dictKeyByVal(SharedLocker.errorlevel,True))
    SharedLocker.lock.release()

    