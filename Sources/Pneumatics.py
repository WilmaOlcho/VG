##Pneumatics.py
from StaticLock import SharedLocker
import configparser
import xml.etree.ElementTree as ET
from TactWatchdog import TactWatchdog as WDT

class Piston(SharedLocker):
    name = ''       #LeftPucher
    type = ''     #double
    model = ''      #IV7870
    vendor = ''     #MetalWork
    sensors = []    #reed in back, reed in front
    valve = []      #valve to control

    def __init__(self, branch, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = branch
        self.parent = parent
        self.valves = []
        self.sensors = []
        for child in self.root.findall('valve'):
            self.valves.append(Valve(child, self))
        for child in self.root.findall('sensor'):
            self.sensors.append(Sensor(child, self))
        self.name = self.root.findall('name')[0].text
        self.type = self.root.findall('type')[0].text
        self.model = self.root.findall('model')[0].text
        self.vendor = self.root.findall('vendor')[0].text

    def controlSequence(self):
        for sensor in self.sensors:
            sensor.controlSequence()
        for valve in self.valves:
            valve.controlSequence()


class Sensor(SharedLocker):
    def __init__(self, branch, parent, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.parent = parent
        self.root = branch
        self.SensorType = self.root.findall('type')[0].text
        self.address = self.root.findall('address')[0].text
        self.voltage = self.root.findall('voltage')[0].text
        self.current = self.root.findall('current')[0].text
        self.action = self.root.findall('action')[0].text

    def controlSequence(self):
        self.lock.acquire()
        cstate = bool(self.GPIO[self.address])
        self.pistons['sensor'+self.action] = cstate
        self.lock.release()

class Coil(SharedLocker):
    def __init__(self, branch, parent, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.parent = parent
        self.timer = None
        self.root = branch
        self.coilType = self.root.findall('type')[0].text
        self.address = self.root.findall('address')[0].text
        self.voltage = self.root.findall('voltage')[0].text
        self.current = self.root.findall('current')[0].text
        self.action = self.root.findall('action')[0].text
        self.nosensor = True if self.root.findall('nosensor')[0].text == 'True' else False
        self.timeout = int(self.root.findall('timeout')[0].text)

    def controlSequence(self):
        self.lock.acquire()
        cstate = bool(self.pistons['sensor'+self.action])
        rstate = bool(self.pistons[self.action])
        self.lock.release()
        if rstate and not cstate:
            self.GPIO[self.address] = True
            self.GPIO['somethingChaged']
            if not self.nosensor and self.timer == None:
                self.timer = WDT(errToRaise = self.action + ' of '+self.parent.parent.name+' time exceeded', errorlevel = 30, limitval = self.timeout)
        else:
            self.GPIO[self.address] = False
            if not isinstance(self.timer,None):
                self.timer.Destruct()


class Valve(SharedLocker):
    valveType = ''
    coils = []
    def __init__(self, branch, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = branch
        for child in self.root.findall('coil'):
            self.coils.append(Coil(child, self))

    def controlSequence(self):
        for coil in self.coils:
            coil.controlSequence()




class PneumaticsVG(SharedLocker):
    def __init__(self, xmlFile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.tree = ET.parse(xmlFile)
            self.root = self.tree.getroot()
            self.parameters = self.tree
            self.Pistons = []
            self.Valves = []
            self.Sensors = []
            for child in self.root.findall('piston'):
                self.Pistons.append(Piston(child, self))
            for child in self.root.findall('valve'):
                self.Valves.append(Valve(child, self))
            for child in self.root.findall('sensor'):
                self.Sensors.append(Sensor(child, self))
            self.lock.acquire()
            self.pistons['Alive'] = True
            self.lock.release()
            self.Alive = True
            self.PneumaticsLoop()
        except Exception as ex:
            self.lock.acquire()
            self.events['Error'] = True
            self.errorlevel[10] = True
            self.shared['Errors'] += '/nPneumaticsVG init error - Error while parsing config file' + ex.__class__ + ex.
            self.lock.release()

    def PneumaticsLoop(self):
        while self.Alive:
            for piston in self.Pistons:
                piston.controlSequence()
            for valve in self.Valves:
                valve.controlSequence()
            for sensor in self.Sensors:
                sensor.controlSequence()
            self.lock.acquire()
            self.Alive = self.pistons['Alive']
            self.lock.release()
       
       
       
       
       
    #   
    #    if len(self.filefeedback):
    #        try:
    #            for section in Parameters.sections():
    #                if 'piston' in section:
    #                    self.Actuators.append(Piston(self.parameters, section))
    #        
    #        finally:
    #            super().__init__(*args, **kwargs)
    #            self.Alive = True
    #            self.lock.acquire()
    #            self.pistons['Alive'] = self.Alive
    #            self.lock.release()
    #    else:
    #        self.lock.acquire()
    #        self.events['Error'] = True
    #        self.errorlevel[10] = True
    #        self.shared['Errors'] += '/nPneumaticsVG init error - Config file not found'
    #        self.lock.release()3

