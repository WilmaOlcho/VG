##Pneumatics.py
from StaticLock import SharedLocker
import configparser
import json
from TactWatchdog import TactWatchdog as WDT

class Pneumatic(object):
    def __init__(self, branch, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = branch
        self.parent = parent
        self.childobjects = []
        self.name = self.root['name']
        self.type = self.root['type']
        self.model = self.root['model']
        self.vendor = self.root['vendor']
        
    def controlSequence(self):
        for child in self.childobjects:
            child.controlSequence()

class PneumaticActive(Pneumatic):
    def __init__(self, branch, parent, *args, **kwargs):
        super().__init__(branch, parent, *args, **kwargs)
        self.address = self.root['address']
        self.voltage = self.root['voltage']
        self.current = self.root['current']
        self.action = self.root['action']

class Piston(Pneumatic, SharedLocker):
    def __init__(self, branch, parent, *args, **kwargs):
        super().__init__(branch, parent, *args, **kwargs)
        for child in self.root['objects']:
            if child['class'] == 'Valve': Class = Valve
            elif child['class'] == 'Sensor': Class = Sensor
            else: continue
            self.childobjects.append(Class(child, self))

class Sensor(PneumaticActive, SharedLocker):
    def controlSequence(self):
        self.lock.acquire()
        cstate = bool(self.GPIO[self.address])
        self.pistons['sensor'+self.action] = cstate
        self.lock.release()

class Coil(PneumaticActive, SharedLocker):
    def __init__(self, branch, parent, *args, **kwargs):
        super().__init__(branch, parent, *args,**kwargs)
        self.timer = WDT()
        self.nosensor = self.root['nosensor']
        self.timeout = self.root['timeout']

    def controlSequence(self):
        self.lock.acquire()
        cstate = bool(self.pistons['sensor'+self.action])
        rstate = bool(self.pistons[self.action])
        self.lock.release()
        if rstate and not cstate:
            self.lock.acquire()
            self.GPIO[self.address] = True
            self.GPIO['somethingChaged']
            self.lock.release()
            if not self.nosensor and self.timer == None:
                self.timer = WDT.WDT(errToRaise = self.action + ' of '+self.parent.parent.name+' time exceeded', errorlevel = 30, limitval = self.timeout)
        else:
            self.lock.acquire()
            self.GPIO[self.address] = False
            self.lock.release()
            if self.timer.active: self.timer.Destruct()

class Valve(Pneumatic, SharedLocker):
    def __init__(self, branch, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for child in self.root['objects']:
            if child['class'] == 'Coil':
                self.childobjects.append(Coil(child, self))

class PneumaticsVG(SharedLocker):
    def __init__(self, jsonFile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.file = open(jsonFile)
            self.config = self.file.read()
            self.file.close()
            self.parameters = json.dumps(self.config)
            self.childobjects = []
            for child in self.parameters['objects']:#root.findall('piston'):
                Class = None
                if child['class'] == 'Piston': Class = Piston
                elif child['class'] == 'Valve': Class = Valve
                elif child['class'] == 'Sensor': Class = Sensor
                else: continue
                self.childobjects.append(Class(child, self))
            self.lock.acquire()
            self.pistons['Alive'] = True
            self.lock.release()
            self.Alive = True
            self.PneumaticsLoop()
        except Exception as ex:
            self.lock.acquire()
            self.events['Error'] = True
            self.errorlevel[10] = True
            self.shared['Errors'] += '/nPneumaticsVG init error - Error while parsing config file' + ex.__class__
            self.lock.release()

    def PneumaticsLoop(self):
        while self.Alive:
            for child in self.childobjects:
                child.controlSequence()
            self.lock.acquire()
            self.Alive = self.pistons['Alive']
            self.lock.release()