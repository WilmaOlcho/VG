from modbusTCPunits import SICKGmod
import json
import csv
from xml.etree.ElementTree import ElementTree as ET

class GMOD(SICKGmod):
    def __init__(self, configFile, *args, **kwargs): #configFile must have path to csv generated in FlexiSoft Designer
        try:
            self.json = json.load(open(configFile))
            self.parameters = self.json.decode()
            self.address = self.parameters['basics']['address']
            self.port = self.parameters['basics']['port']
            super().__init__(self.address, self.port, *args,**kwargs)
        except:
            pass