import json
from Sources.misc import ErrorEventWrite
from Sources.TactWatchdog import TactWatchdog as WDT

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
                self.control = {
                    'homing':False,
                    'stepping':False,
                    'running':False,
                    'runningbak':False,
                    'resetting':False,
                    'stopping':False,
                    'activating':False}
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
        lockerinstance[0].lock.acquire()
        WDTActive = 'WDTServo Homing Time exceeded' in lockerinstance[0].wdt
        lockerinstance[0].lock.release()
        if self.control['homing']:
            lockerinstance[0].lock.acquire()
            GPIOrefreshed = not lockerinstance[0].GPIO['somethingChanged']
            lockerinstance[0].lock.release()
            if GPIOrefreshed:
                if WDTActive:
                    lockerinstance[0].lock.acquire()
                    inAPosition = not lockerinstance[0].GPIO[self.coinAddress]
                    lockerinstance[0].lock.release()
                    if inAPosition:
                        self.control['homing'] = False
                        lockerinstance[0].lock.acquire()
                        lockerinstance[0].servo['homing'] = False
                        lockerinstance[0].servo['positionNumber'] = 0
                        lockerinstance[0].events['ServoHomingComplete'] = True
                        lockerinstance[0].lock.release()
                else:
                    self.stop(lockerinstance)
                    ErrorEventWrite(lockerinstance,'Servo is forced to stop')
        else:
            lockerinstance[0].lock.acquire()
            if not lockerinstance[0].GPIO[self.homingAddress]:
                lockerinstance[0].GPIO[self.homingAddress] = True
                lockerinstance[0].GPIO['somethingChanged'] = True
            if lockerinstance[0].GPIO[self.coinAddress]: self.control['homing'] = True
            lockerinstance[0].lock.release()
            if not WDTActive and self.control['homing']:
                WDT.WDT(lockerinstance, scale = 's',limitval = 60, eventToCatch='ServoHomingComplete', errToRaise='Servo Homing Time exceeded', errorlevel=10)

            
    def step(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        WDTActive = 'WDTServo Step Time exceeded' in lockerinstance[0].wdt
        lockerinstance[0].lock.release()
        if self.control['stepping']:
            lockerinstance[0].lock.acquire()
            GPIOrefreshed = not lockerinstance[0].GPIO['somethingChanged']
            lockerinstance[0].lock.release()
            if GPIOrefreshed:
                if WDTActive:
                    lockerinstance[0].lock.acquire()
                    inAPosition = not lockerinstance[0].GPIO[self.coinAddress]
                    lockerinstance[0].lock.release()
                    if inAPosition:
                        self.control['stepping'] = False
                        lockerinstance[0].lock.acquire()
                        lockerinstance[0].servo['step'] = False
                        pos = lockerinstance[0].servo['positionNumber']
                        lockerinstance[0].servo['positionNumber'] = (pos+1) if pos < 2 else 0
                        lockerinstance[0].events['ServoStepComplete'] = True
                        lockerinstance[0].lock.release()
                else:
                    self.control['stepping'] = False
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].servo['step'] = False
                    lockerinstance[0].servo['positionNumber'] = -1
                    lockerinstance[0].lock.release()
                    self.stop(lockerinstance)
                    ErrorEventWrite(lockerinstance,'Servo is forced to stop')
        else:
            lockerinstance[0].lock.acquire()
            if not lockerinstance[0].GPIO[self.stepAddress]:
                lockerinstance[0].GPIO[self.stepAddress] = True
                lockerinstance[0].GPIO['somethingChanged'] = True
            if lockerinstance[0].GPIO[self.coinAddress]: self.control['stepping'] = True
            lockerinstance[0].lock.release()
            if not WDTActive and self.control['stepping']:
                WDT.WDT(lockerinstance, scale = 's',limitval = 10, eventToCatch='ServoStepComplete', errToRaise='Servo Step Time exceeded', errorlevel=10)

    def reset(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        WDTActive = 'WDTServo Resetting' in lockerinstance[0].wdt
        lockerinstance[0].lock.release()
        if self.control['running']:
            self.stop(lockerinstance)
        if self.control['resetting']:
            if not WDTActive:
                if self.control['runningbak']:
                    self.run(lockerinstance)
                self.control['resetting'] = False
                lockerinstance[0].lock.acquire()
                lockerinstance[0].GPIO[self.resetAddress] = False
                lockerinstance[0].servo['reset'] = False
                lockerinstance[0].GPIO['somethingChanged'] = True
                lockerinstance[0].lock.release()
        else:
            if WDTActive:
                self.control['resetting'] = True
                self.control['runningbak'] = self.control['running']
            else:
                lockerinstance[0].lock.acquire()
                lockerinstance[0].GPIO[self.resetAddress] = True
                lockerinstance[0].GPIO['somethingChanged'] = True
                lockerinstance[0].lock.release()
                WDT.WDT(lockerinstance, scale = 's', noerror = True, limitval = 4, errToRaise='Servo Resetting')

    def stop(self, lockerinstance):
        if self.control['stopping']:
            lockerinstance[0].lock.acquire()
            GPIOrefreshed = not lockerinstance[0].GPIO['somethingChanged']
            lockerinstance[0].lock.release()
            if GPIOrefreshed:
                self.control['running'] = False
                self.control['stopping'] = False
                lockerinstance[0].lock.acquire()
                lockerinstance[0].servo['stop'] = False
                lockerinstance[0].lock.release()
        else:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.activeAddress] = False
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].servo['run'] = False
            lockerinstance[0].servo['step'] = False
            lockerinstance[0].servo['homing'] = False
            lockerinstance[0].lock.release()
            self.control['stopping'] = True

    def run(self, lockerinstance):
        if self.control['activating']:
            lockerinstance[0].lock.acquire()
            GPIOrefreshed = not lockerinstance[0].GPIO['somethingChanged']
            lockerinstance[0].lock.release()
            if GPIOrefreshed:
                self.control['activating'] = False
                self.control['running'] = True
                lockerinstance[0].lock.acquire()
                lockerinstance[0].servo['run'] = False
                lockerinstance[0].lock.release()
        else:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.activeAddress] = True
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
            self.control['activating'] = True
        
    def IO(self, lockerinstance):
        if self.control['running'] or self.control['activating']:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['active'] = lockerinstance[0].GPIO[self.sreadyAddress]
            lockerinstance[0].lock.release()
        else:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['step'] = False
            lockerinstance[0].servo['homing'] = False
            lockerinstance[0].lock.release()
        lockerinstance[0].lock.acquire()
        lockerinstance[0].servo['moving'] = lockerinstance[0].GPIO[self.tgonAddress]
        changed = False
        if not lockerinstance[0].GPIO['somethingChanged']: 
            if not self.control['stepping'] and lockerinstance[0].GPIO[self.stepAddress] and not lockerinstance[0].servo['step']:
                changed = True
                lockerinstance[0].GPIO[self.stepAddress] = False
            if not self.control['homing'] and lockerinstance[0].GPIO[self.homingAddress] and not lockerinstance[0].servo['homing']:
                changed = True
                lockerinstance[0].GPIO[self.homingAddress] = False
        if lockerinstance[0].GPIO[self.coinAddress] or not lockerinstance[0].GPIO[self.activeAddress]:
            if lockerinstance[0].GPIO[self.homingAddress] or ((lockerinstance[0].GPIO[self.stepAddress] or lockerinstance[0].GPIO[self.resetAddress]) and not lockerinstance[0].GPIO[self.tgonAddress]): changed = True
            lockerinstance[0].GPIO[self.homingAddress] = lockerinstance[0].GPIO[self.resetAddress] = lockerinstance[0].GPIO[self.stepAddress] = False
        if changed: lockerinstance[0].GPIO['somethingChanged'] = True
        lockerinstance[0].lock.release()