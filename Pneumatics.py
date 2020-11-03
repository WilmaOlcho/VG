##Pneumatics.py


class Piston:
    name = ''       #LeftPucher
    acting = ''     #double
    model = ''      #IV7870
    vendor = ''     #MetalWork
    sensors = []    #reed in back, reed in front
    valve = []      #valve to control

    def __init__():
        pass

class Sensor:
    sensorType = ''
    adress = 0
    active = False
    def __init__():
        pass

class PressureSensor(Sensor):
    def __init__():
        pass

class Reed(Sensor):
    def __init__():
        pass

class Coil():
    coilType = 'DC'
    adress = 0
    voltage = 24
    current = 200/1000
    def __init__():

class Valve():
    valveType = ''
    coils = []

