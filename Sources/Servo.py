import json
from Sources import ErrorEventWrite
from Sources.TactWatchdog import TactWatchdog as WDT
from Sources import EventManager

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
        
    def servoloop(self, lockerinstance):
        control = {'run':False, 'step':False, 'homing':False, 'stop':False, 'reset':False}
        while self.Alive:
            lockerinstance[0].lock.acquire()
            for key in control.keys():
                control[key] = lockerinstance[0].servo[key]
                if control[key]:
                    lockerinstance[0].servo[key] = False
            self.Alive = lockerinstance[0].servo['Alive']
            lockerinstance[0].lock.release()
            if control['homing']: self.homing(lockerinstance)
            if control['step']: self.step(lockerinstance)
            if control['reset']: self.reset(lockerinstance)
            if control['run']: self.run(lockerinstance)
            if control['stop']: self.stop(lockerinstance)
            self.IO(lockerinstance)

    def homing(self, lockerinstance):
        def funconstart(object = self, lockerinstance = lockerinstance):
            EventManager.AdaptEvent(lockerinstance, input = object.coinAddress, event = 'ServoMoving')
        def funconloop(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.homingAddress] = True
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        def releasing(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.homingAddress] = False
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        def funconcatchServoEnd(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['positionNumber'] = 0
            lockerinstance[0].lock.release()
        def funconcatch(object = self, lockerinstance = lockerinstance):
            EventManager.AdaptEvent(lockerinstance, input = '-'+object.coinAddress, event = 'ServoHomingComplete')
            WDT.WDT(lockerinstance, additionalFuncOnExceed = funconexceed, additionalFuncOnLoop = releasing, additionalFuncOnCatch = funconcatchServoEnd, scale = 's',limitval = 30, eventToCatch='ServoHomingComplete', errToRaise='Servo Homing Time Exceeded')
        def funconexceed(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['positionNumber'] = -1
            lockerinstance[0].lock.release()
            releasing(lockerinstance)
            object.stop(lockerinstance)
            EventManager.DestroyEvent(lockerinstance, event = 'ServoHomingComplete')
            EventManager.DestroyEvent(lockerinstance, event = 'ServoMoving')
            ErrorEventWrite(lockerinstance,'Servo is forced to stop')
        WDT.WDT(lockerinstance, additionalFuncOnStart = funconstart, additionalFuncOnExceed = funconexceed, additionalFuncOnLoop = funconloop, additionalFuncOnCatch = funconcatch, scale = 's',limitval = 5, eventToCatch='ServoMoving', errToRaise='Servo Starting Time Exceeded')
            
    def step(self, lockerinstance):
        def funconstart(object = self, lockerinstance = lockerinstance):
            EventManager.AdaptEvent(lockerinstance, input = object.coinAddress, event = 'ServoMoving')
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
        def funconcatchServoEnd(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            pos = lockerinstance[0].servo['positionNumber']
            lockerinstance[0].servo['positionNumber'] = (pos+1) if pos < 2 else 0
            lockerinstance[0].lock.release()
        def funconcatch(object = self, lockerinstance = lockerinstance):
            EventManager.AdaptEvent(lockerinstance, input = '-'+object.coinAddress, event = 'ServoStepComplete')
            WDT.WDT(lockerinstance, additionalFuncOnExceed = funconexceed, additionalFuncOnLoop = releasing, additionalFuncOnCatch = funconcatchServoEnd, scale = 's',limitval = 30, eventToCatch='ServoStepComplete', errToRaise='Servo Stepping Time Exceeded')
        def funconexceed(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['positionNumber'] = -1
            lockerinstance[0].lock.release()
            releasing(lockerinstance)
            object.stop(lockerinstance)
            EventManager.DestroyEvent(lockerinstance, event = 'ServoStepComplete')
            EventManager.DestroyEvent(lockerinstance, event = 'ServoMoving')
            ErrorEventWrite(lockerinstance,'Servo is forced to stop')
        WDT.WDT(lockerinstance, additionalFuncOnStart = funconstart, additionalFuncOnExceed = funconexceed, additionalFuncOnLoop = funconloop, additionalFuncOnCatch = funconcatch, scale = 's',limitval = 5, eventToCatch='ServoMoving', errToRaise='Servo Starting Time Exceeded')
            
    def reset(self, lockerinstance):
        def funconexceedrelease(object = self, lockerinstance = lockerinstance, running = False):
            if running: object.run(lockerinstance)
        def funconlooprelease(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.resetAddress] = False
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        def funconexceed(object = self, lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            running = lockerinstance[0].GPIO[self.activeAddress]
            lockerinstance[0].lock.release()
            if running: object.stop(lockerinstance)
            WDT.WDT(lockerinstance, additionalFuncOnLoop = funconlooprelease, additionalFuncOnExceed = lambda obj = object, lck = lockerinstance, rn = running:funconexceedrelease(object = obj, lockerinstance=lck, running=rn), scale = 's', noerror = True, limitval = 2, errToRaise='Servo Resetting Release')
        def funconloop(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.resetAddress] = True
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        WDT.WDT(lockerinstance, additionalFuncOnLoop = funconloop, additionalFuncOnExceed = funconexceed, scale = 's', noerror = True, limitval = 2, errToRaise='Servo Resetting')

    def stop(self, lockerinstance):
        def funconloop(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.activeAddress] = False
            lockerinstance[0].GPIO[self.stepAddress] = False
            lockerinstance[0].GPIO[self.homingAddress] = False
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        WDT.WDT(lockerinstance, additionalFuncOnLoop = funconloop, scale = 's', noerror = True, limitval = 2, errToRaise='Servo Stopping')

    def run(self, lockerinstance):
        def funconloop(lockerinstance = lockerinstance):
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.activeAddress] = True
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
        WDT.WDT(lockerinstance, additionalFuncOnLoop = funconloop, scale = 's', noerror = True, limitval = 2, errToRaise='Servo Running')
       
    def IO(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        lockerinstance[0].servo['active'] = lockerinstance[0].GPIO[self.sreadyAddress]
        lockerinstance[0].lock.release()

