import json
from Sources.misc import ErrorEventWrite
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources.Kawasaki import EventManager

class Servo(object):
    def __init__(self, lockerinstance, jsonfile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Alive = True
        lockerinstance[0].lock.acquire()
        lockerinstance[0].servo['Alive'] = True
        lockerinstance[0].lock.release()
        while self.Alive:
            try:
                self.settings = json.load(open(jsonfile,'r'))
            except Exception as e:
                ErrorEventWrite(lockerinstance, "Servo.__init__ Error: Can't load json file " + str(e))
            else:
                for item in self.settings['inputs'].items():
                    if item[1]['Name'] == 'N-CL': self.homingAddress = item[1]['Address']
                    if item[1]['Name'] == 'S-ON': self.activeAddress = item[1]['Address']
                    if item[1]['Name'] == 'P-CON': self.stepAddress = item[1]['Address']
                    if item[1]['Name'] == 'ALMRST': self.resetAddress = item[1]['Address']
                for item in self.settings['outputs'].items():
                    if item[1]['Name'] == '/COIN/VMCP': self.coinAddress = item[1]['Address']
                    if item[1]['Name'] == '/TGON': self.tgonAddress = item[1]['Address']
                    if item[1]['Name'] == '/S-RDY': self.sreadyAddress = item[1]['Address']
                    if item[1]['Name'] == '/CLT': self.cltAddress = item[1]['Address']
                self.servoloop(lockerinstance)
            lockerinstance[0].lock.acquire()
            self.Alive = lockerinstance[0].servo['Alive']
            lockerinstance[0].lock.release()
            if not self.Alive: break
        
    def servoloop(self, lockerinstance):
        while self.Alive:
            lockerinstance[0].lock.acquire()
            homing, step, reset = lockerinstance[0].servo['homing'], lockerinstance[0].servo['step'], lockerinstance[0].servo['reset']
            run, stop = lockerinstance[0].servo['run'], lockerinstance[0].servo['stop']
            lockerinstance[0].lock.release()
            if homing: self.homing(lockerinstance)
            if step: self.step(lockerinstance)
            if reset: self.reset(lockerinstance)
            if run: self.run(lockerinstance)
            if stop: self.stop(lockerinstance)
            self.IO(lockerinstance)
            lockerinstance[0].lock.acquire()
            self.Alive = lockerinstance[0].servo['Alive']
            lockerinstance[0].lock.release()

    def homing(self, lockerinstance):
        def funconstart(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['homing'] = False
            lockerinstance[0].lock.release()
            EventManager.AdaptEvent(lockerinstance, input = self.coinAddress, edge = 'falling', event = 'ServoHomingComplete')
        def funconloop(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.homingAddress] = True
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        def funconcatch(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['homing'] = False
            lockerinstance[0].servo['positionNumber'] = 0
            lockerinstance[0].lock.release()
            def releasing(object = self, lockerinstance = lockerinstance):
                lockerinstance[0].lock.acquire()
                lockerinstance[0].GPIO[self.homingAddress] = False
                lockerinstance[0].GPIO['somethingChanged'] = True
                lockerinstance[0].lock.release()
                WDT.WDT(lockerinstance, scale = 's',limitval = 4, additionalFuncOnExceed = releasing, errToRaise='ServoReleasing', noerror = True)
        def funconexceed(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['homing'] = False
            lockerinstance[0].servo['positionNumber'] = -1
            lockerinstance[0].lock.release()
            object.stop(lockerinstance)
            ErrorEventWrite(lockerinstance,'Servo is forced to stop')
        WDT.WDT(lockerinstance, additionalFuncOnStart = funconstart, additionalFuncOnExceed = funconexceed, additionalFuncOnLoop = funconloop, additionalFuncOnCatch = funconcatch, scale = 's',limitval = 30, eventToCatch='ServoHomingComplete', errToRaise='Servo Homing Time exceeded')
            
    def step(self, lockerinstance):
        def funconstart(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['step'] = False
            lockerinstance[0].lock.release()
            EventManager.AdaptEvent(lockerinstance, input = self.coinAddress, edge = 'falling', event = 'ServoStepComplete')
        def funconloop(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.stepAddress] = True
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        def releasing(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.stepAddress] = False
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        def funconcatch(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            pos = lockerinstance[0].servo['positionNumber']
            lockerinstance[0].servo['positionNumber'] = (pos+1) if pos < 2 else 0
            lockerinstance[0].lock.release()
            WDT.WDT(lockerinstance, scale = 's', limitval = 4, additionalFuncOnExceed = releasing, errToRaise='ServoReleasing', noerror = True)
        def funconexceed(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['step'] = False
            lockerinstance[0].servo['positionNumber'] = -1
            lockerinstance[0].lock.release()
            releasing(lockerinstance)
            object.stop(lockerinstance)
            ErrorEventWrite(lockerinstance,'Servo is forced to stop')
        WDT.WDT(lockerinstance, additionalFuncOnStart = funconstart, additionalFuncOnExceed = funconexceed, additionalFuncOnLoop = funconloop, additionalFuncOnCatch = funconcatch, scale = 's',limitval = 10, eventToCatch='ServoStepComplete', errToRaise='Servo Step Time exceeded')

    def reset(self, lockerinstance):
        def funconstart(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['reset'] = False
            lockerinstance[0].lock.release()
        def funconexceed(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            running = lockerinstance[0].GPIO[self.activeAddress]
            lockerinstance[0].lock.release()
            if running: object.stop(lockerinstance)
            def funconexceedrelease(object = self, lockerinstance = lockerinstance, running = running):
                if running: object.run(lockerinstance)
                return False
            def funconlooprelease(lockerinstance = lockerinstance):
                lockerinstance[0].lock.acquire()
                lockerinstance[0].GPIO[self.resetAddress] = False
                lockerinstance[0].GPIO['somethingChanged'] = True
                lockerinstance[0].lock.release()
            WDT.WDT(lockerinstance, additionalFuncOnLoop = funconlooprelease, additionalFuncOnExceed = funconexceedrelease, scale = 's', noerror = True, limitval = 4, errToRaise='Servo Resetting Release')
            return False
        def funconloop(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.resetAddress] = True
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        WDT.WDT(lockerinstance, additionalFuncOnStart = funconstart, additionalFuncOnLoop = funconloop, additionalFuncOnExceed = funconexceed, scale = 's', noerror = True, limitval = 4, errToRaise='Servo Resetting')

    def stop(self, lockerinstance):
        def funconstart(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['run'] = False
            lockerinstance[0].servo['step'] = False
            lockerinstance[0].servo['homing'] = False
            lockerinstance[0].servo['stop'] = False
            lockerinstance[0].lock.release()
        def funconloop(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.activeAddress] = False
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        def funconexceed(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['stop'] = False
            lockerinstance[0].lock.release()
        WDT.WDT(lockerinstance, additionalFuncOnStart = funconstart, additionalFuncOnLoop = funconloop, additionalFuncOnExceed = funconexceed, scale = 's', noerror = True, limitval = 4, errToRaise='Servo Stopping')

    def run(self, lockerinstance):
        def funconstart(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['run'] = False
            lockerinstance[0].lock.release()
        def funconloop(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.activeAddress] = True
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        def funconexceed(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['run'] = False
            lockerinstance[0].lock.release()
        WDT.WDT(lockerinstance, additionalFuncOnStart = funconstart, additionalFuncOnLoop = funconloop, additionalFuncOnExceed = funconexceed, scale = 's', noerror = True, limitval = 4, errToRaise='Servo Running')
       
    def IO(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        lockerinstance[0].servo['active'] = lockerinstance[0].GPIO[self.sreadyAddress]
        lockerinstance[0].lock.release()

