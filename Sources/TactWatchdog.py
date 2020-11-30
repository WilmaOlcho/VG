import time
from threading import Thread
from misc import BlankFunc, writeInLambda
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
                additionalFuncOnStart = BlankFunc,
                additionalFuncOnLoop = BlankFunc,
                additionalFuncOnCatch = BlankFunc,
                additionalFuncOnExceed = BlankFunc,
                *args, **kwargs):
        additionalFuncOnStart(*args, **kwargs)
        self.setpoint()
        limitval *= self.scaleMultiplier[scale]
        while True:
            additionalFuncOnLoop(*args, **kwargs)
            SharedLocker.lock.acquire()
            SharedLocker.shared['TactWDT'] |= True
            if eventToCatch[0] == '-':
                event = not(SharedLocker.shared['Events'][eventToCatch[1:]])
            else:
                event = SharedLocker.shared['Events'][eventToCatch]
            SharedLocker.lock.release()
            if event:
                additionalFuncOnCatch(*args, **kwargs)
                break
            if self.elapsed() >= limitval:
                SharedLocker.lock.acquire()
                SharedLocker.shared['Errors'] += errToRaise
                SharedLocker.shared['Errorlevel'] += ','+str(errorlevel)
                print(SharedLocker.shared['Errorlevel'])
                SharedLocker.lock.release()
                additionalFuncOnExceed(*args, **kwargs)
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
            additionalFuncOnStart = BlankFunc,
            additionalFuncOnLoop = BlankFunc,
            additionalFuncOnCatch = BlankFunc,
            additionalFuncOnExceed = BlankFunc,
            *args, **kwargs):
        WDT = cli()
        thread = Thread(target=WDT.WDTloop, args = (limitval,
                                                    errToRaise,
                                                    caption, scale, errorlevel,
                                                    eventToCatch,
                                                    additionalFuncOnStart,
                                                    additionalFuncOnLoop,
                                                    additionalFuncOnCatch,
                                                    additionalFuncOnExceed, *args), daemon = False)
        thread.start()

if __name__=='__main__': ##Test
    cinst = SharedLocker()
    TactWatchdog.WDT(errToRaise = 'ERR1', limitval = 3)
    TactWatchdog.WDT(caption = 'TACT1EXCEEDED', limitval = 8)
    TactWatchdog.WDT(errToRaise = 'Servo', limitval = 10000, scale = 'ms', errorlevel = 3)
    TactWatchdog.WDT(caption = 'ESTUN working', limitval = 20, scale = 's',eventToCatch = '-RobotMoving', additionalFuncOnCatch = lambda: cinst.WithLock(writeInLambda,cinst.shared['Events']['RobotMoving'], False))
    TactWatchdog.WDT(errToRaise = 'ERR2', limitval = 10, scale = 's')
    TactWatchdog.WDT(limitval = 4, scale = 's')
    TactWatchdog.WDT(errToRaise = 'ERR3', limitval = 4, scale = 's', additionalFuncOnExceed = lambda: cinst.WithLock(writeInLambda,cinst.shared['Events']['ack'], True))
    dt = True
    last = ''
    while dt:
        cinst.lock.acquire()
        dt = cinst.shared['TactWDT']
        cinst.shared['TactWDT'] = False
        news = cinst.shared['Errors']
        if last != news:
            print(news.replace(last,'',1))
            last = cinst.shared['Errors']
        cinst.lock.release()
    cinst.lock.acquire()
    errorlevelList = set(cinst.shared['Errorlevel'][1:].split(','))
    cinst.lock.release()
    print(errorlevelList)

    