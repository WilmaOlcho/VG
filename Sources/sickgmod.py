from modbusTCPunits import SICKGmod
import json
import csv
from xml.etree.ElementTree import ElementTree as ET

class GMOD(SICKGmod):
    def __init__(self, configFile, *args, **kwargs): #configFile must have path to csv generated in FlexiSoft Designer
        try:
            self.parameters = json.load(open(configFile))
            self.address = self.parameters['basics']['address']
            self.port = self.parameters['basics']['port']
            super().__init__(self.address, self.port, *args,**kwargs)
        except json.JSONDecodeError:
            self.lock.acquire()
            self.events['Error'] = True
            self.errorlevel[10] = True
            self.shared['Errors'] += '/nGMOD init error - Error while parsing config file'
            self.lock.release()
        except Exception as ex:
            self.lock.acquire()
            self.events['Error'] = True
            self.errorlevel[10] = True
            self.shared['Errors'] += '/nGMOD init error - ' + ex.__class__
            self.lock.release()
        try:
            self.csvfile = self.parameters['csv']
            self.FSDcsv = csv.reader(open(self.csvfile))
            self.IOBonding = []
            for i, row in enumerate(self.FSDcsv):
                self.IOBonding.append([])
                for column in row[0].split(';'):
                    self.IOBonding[i].append(column)        
        except:
            self.lock.acquire()
            self.events['Error'] = True
            self.errorlevel[10] = True
            self.shared['Errors'] += '/nGMOD init error - CSV file parsing raised exception' + ex.__class__
            self.lock.release()
        try:
            dictionaryForStaticLock = {}
            for byte in self.IOBonding:
                if len(byte[1]) and '.' in byte[0]:
                    dictionaryForStaticLock[byte[0]] = byte[1]
            if self.SICKGMOD0 == None:
                SharedLocker.SICKGMOD0 = Manager().dict({**dictionaryForStaticLock,'dict':dictionaryForStaticLock})
        except:
            pass