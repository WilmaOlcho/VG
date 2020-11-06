##Pneumatics.py


class Piston:
    name = ''       #LeftPucher
    acting = ''     #double
    model = ''      #IV7870
    vendor = ''     #MetalWork
    sensors = []    #reed in back, reed in front
    valve = []      #valve to control

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Sensor:
    sensorType = ''
    adress = 0
    active = False
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

class PressureSensor(Sensor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

class Reed(Sensor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

class Coil:
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.coilType = 'DC'
        self.adress = 0
        self.voltage = 24
        self.current = 200/1000

class Valve:
    valveType = ''
    coils = []

