##Pneumatics.py


class Piston:
    name = ''       #LeftPucher
    acting = ''     #double
    model = ''      #IV7870
    vendor = ''     #MetalWork
    sensors = []    #reed in back, reed in front
    valve = []      #valve to control

    def __init__():
        super().__init()

class Sensor:
    sensorType = ''
    adress = 0
    active = False
    def __init__():
        super().__init()

class PressureSensor(Sensor):
    def __init__():
        super().__init()

class Reed(Sensor):
    def __init__():
        super().__init()

class Coil():
    coilType = 'DC'
    adress = 0
    voltage = 24
    current = 200/1000
    def __init__():
        super().__init()

class Valve():
    valveType = ''
    coils = []

