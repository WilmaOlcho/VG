##Pneumatics.py
import json
from Sources.TactWatchdog import TactWatchdog as WDT

class Pneumatic(object):
    def __init__(self, lockerinstance, branch, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = {**branch}
        self.parent = parent
        self.childobjects = []
        self.name = self.root['name']
        self.type = self.root['type']
        self.model = self.root['model']
        self.vendor = self.root['vendor']
        
    def controlSequence(self, lockerinstance):
        for child in self.childobjects:
            child.controlSequence(lockerinstance)

class PneumaticActive(Pneumatic):
    def __init__(self, lockerinstance, branch, parent, *args, **kwargs):
        super().__init__(lockerinstance, branch, parent, *args, **kwargs)
        self.address = self.root['address']
        self.voltage = self.root['voltage']
        self.current = self.root['current']
        self.action = self.root['action']

class Piston(Pneumatic):
    def __init__(self, lockerinstance, branch, parent, *args, **kwargs):
        super().__init__(lockerinstance, branch, parent, *args, **kwargs)
        for child in self.root['objects']:
            if child['class'] == 'Valve': Class = Valve
            elif child['class'] == 'Sensor': Class = Sensor
            else: continue
            try:
                self.childobjects.append(Class(lockerinstance, child, self))
            except:
                errstring = ('\nPiston init error - Error while creating subobject: ' + str(child['class'])) if Class is not None else ('\nParent = ' + str(self))
                lockerinstance[0].lock.acquire()
                lockerinstance[0].events['Error'] = True
                lockerinstance[0].errorlevel[10] = True
                if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring
                lockerinstance[0].lock.release()

class Sensor(PneumaticActive):
    def __init__(self, lockerinstance, branch, parent, *args, **kwargs):
        super().__init__(lockerinstance, branch, parent, *args,**kwargs)
        if 'tandem' in self.root.keys():
            self.tandem = self.root['tandem']
        else:
            self.tandem = False
            
    def controlSequence(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        cstate = bool(lockerinstance[0].GPIO[self.address])
        if self.tandem: cstate = cstate & lockerinstance[0].pistons['sensor'+self.tandem]
        lockerinstance[0].pistons['sensor'+self.action] = cstate
        lockerinstance[0].lock.release()

class Coil(PneumaticActive):
    def __init__(self, lockerinstance, branch, parent, *args, **kwargs):
        super().__init__(lockerinstance, branch, parent, *args,**kwargs)
        self.timer = ''
        self.nosensor = self.root['nosensor']
        self.timeout = self.root['timeout']

    def controlSequence(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        cstate = lockerinstance[0].pistons['sensor'+self.action] if not self.nosensor else False
        rstate = lockerinstance[0].pistons[self.action]
        timers = list(lockerinstance[0].wdt)
        lockerinstance[0].lock.release()
        if rstate and not cstate:
            #print(self.action)
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.address] = True
            lockerinstance[0].GPIO['somethingChanged'] = True
            lockerinstance[0].lock.release()
            if not self.nosensor and not self.timer in timers:
                self.timer = WDT.WDT(lockerinstance, errToRaise = self.action + ' of '+self.parent.parent.name+' time exceeded', scale = 's', errorlevel = 30, limitval = self.timeout)
        else:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].GPIO[self.address] = False
            lockerinstance[0].lock.release()
            if self.timer in timers:
                lockerinstance[0].lock.acquire()
                lockerinstance[0].wdt.remove(self.timer)
                lockerinstance[0].lock.release()

class Valve(Pneumatic):
    def __init__(self, lockerinstance, branch, parent, *args, **kwargs):
        super().__init__(lockerinstance, branch, parent, *args, **kwargs)
        for child in self.root['objects']:
            Class = None
            if child['class'] == 'Coil': Class = Coil
            try:
                self.childobjects.append(Class(lockerinstance, child, self))
            except:
                errstring = ('\nValve init error - Error while creating subobject: ' + str(child['class'])) if Class is not None else ('\nParent = ' + str(self))
                lockerinstance[0].lock.acquire()
                lockerinstance[0].events['Error'] = True
                lockerinstance[0].errorlevel[10] = True
                if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring
                lockerinstance[0].lock.release()

class PneumaticsVG(object):
    def __init__(self, lockerinstance, jsonFile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.parameters = json.load(open(jsonFile))
        except:
            errstring = '\nPneumaticsVG init error - Error while parsing config file'
            lockerinstance[0].lock.acquire()
            lockerinstance[0].events['Error'] = True
            lockerinstance[0].errorlevel[10] = True
            if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring
            lockerinstance[0].lock.release()
        else:
            self.childobjects = []
            for child in self.parameters['objects']:#root.findall('piston'):
                Class = None
                if child['class'] == 'Piston': Class = Piston
                elif child['class'] == 'Valve': Class = Valve
                elif child['class'] == 'Sensor': Class = Sensor
                else: continue
                try:
                    self.childobjects.append(Class(lockerinstance, child, self))
                except:
                    errstring = ('\nPneumaticsVG init error - Error while creating subobject: ' + str(child['class'])) if Class is not None else ('\nParent = ' + str(self))
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].events['Error'] = True
                    lockerinstance[0].errorlevel[10] = True
                    if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring
                    lockerinstance[0].lock.release()
            lockerinstance[0].lock.acquire()
            lockerinstance[0].pistons['Alive'] = True
            lockerinstance[0].lock.release()
            self.Alive = True
            self.PneumaticsLoop(lockerinstance)


    def PneumaticsLoop(self, lockerinstance):
        while self.Alive:
            for child in self.childobjects:
                child.controlSequence(lockerinstance)
            lockerinstance[0].lock.acquire()
            self.Alive = lockerinstance[0].pistons['Alive']
            lockerinstance[0].lock.release()