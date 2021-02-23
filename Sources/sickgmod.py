from Sources.modbusTCPunits import SICKGmod
from Sources import ErrorEventWrite, dictKeyByVal
import json
import csv
import re
from xml.etree.ElementTree import ElementTree as ET

class GMOD(SICKGmod):
    def __init__(self, lockerinstance, configFile, *args, **kwargs): #configFile must have path to csv generated in FlexiSoft Designer
        while True:
            try:
                self.parameters = json.load(open(configFile))
                self.address = self.parameters['basics']['address']
                self.port = self.parameters['basics']['port']
                super().__init__(lockerinstance, self.address, self.port, *args,**kwargs)
            except json.JSONDecodeError:
                errstring = '\nGMOD init error - Error while parsing config file'
                ErrorEventWrite(lockerinstance, errstring)
            except Exception as e:
                errstring = '\nGMOD init error - ' + str(e)
                ErrorEventWrite(lockerinstance, errstring)
            else:
                try:
                    inputscsvfile = self.parameters['inputscsv']
                    outputscsvfile = self.parameters['outputscsv']
                    inputscsv = csv.reader(open(inputscsvfile))
                    outputscsv = csv.reader(open(outputscsvfile))
                    self.inputs = []
                    self.outputs = []
                    for row in inputscsv:
                        self.inputs.append([*row])
                    for row in outputscsv:
                        self.outputs.append([*row])
                except Exception as e:
                    errstring = '\nGMOD init error - CSV file parsing raised exception ' + str(e)
                    ErrorEventWrite(lockerinstance, errstring)
                else:
                    try:
                        for entry in self.inputs:
                            entry = entry[0].split(';')
                            if len(entry)>1:
                                if entry[1] and '.' in entry[0]:
                                    lockerinstance[0].lock.acquire()
                                    lockerinstance[0].SICKGMOD0['inputs'][entry[0]] = entry[1]
                                    lockerinstance[0].SICKGMOD0['inputmap'][entry[0]] = False
                                    lockerinstance[0].lock.release()
                        for entry in self.outputs:
                            entry = entry[0].split(';')
                            if len(entry)>1:
                                if entry[1] and '.' in entry[0]:
                                    lockerinstance[0].lock.acquire()
                                    lockerinstance[0].SICKGMOD0['outputs'][entry[0]] = entry[1]
                                    lockerinstance[0].SICKGMOD0['outputmap'][entry[0]] = False
                                    lockerinstance[0].lock.release()
                    except Exception as e:
                        errstring = '\nGMOD init error - extending DictProxy failed ' + str(e)
                        ErrorEventWrite(lockerinstance, errstring)
                    else:
                        try:
                            self.Alive = True
                            lockerinstance[0].lock.acquire()
                            lockerinstance[0].SICKGMOD0['Alive'] = True
                            lockerinstance[0].lock.release()
                        except:
                            errstring = 'GMOD error ' + str(e)
                            ErrorEventWrite(lockerinstance, errstring)
                        else:
                            self.loop(lockerinstance)
            lockerinstance[0].lock.acquire()
            letdie = not lockerinstance[0].SICKGMOD0['Alive']
            letdie |= lockerinstance[0].events['closeApplication']
            lockerinstance[0].lock.release()
            if letdie: break
    
    def loop(self, lockerinstance):
        while self.Alive:
            self.retrieveinputs(lockerinstance)
            self.retrieveoutputs(lockerinstance)
            self.safetysignals(lockerinstance)
            lockerinstance[0].lock.acquire()
            self.Alive = lockerinstance[0].SICKGMOD0['Alive']
            lockerinstance[0].lock.release()

    def retrieveinputs(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        itemmap = lockerinstance[0].SICKGMOD0['inputmap'].keys()
        lockerinstance[0].lock.release()
        for item in itemmap:
            positionInDatablock = item.split('.')
            address = 8*int(re.findall(r'\d+',positionInDatablock[0])[0])+int(re.findall(r'\d+',positionInDatablock[1])[0])
            try:
                result = self.read_coils(address)
            except Exception as e:
                errstring = "\nGMOD error - can't retrieve inputs " + str(e)
                ErrorEventWrite(lockerinstance, errstring)
            else:
                lockerinstance[0].lock.acquire()
                lockerinstance[0].SICKGMOD0['inputmap']['item'] = result
                lockerinstance[0].lock.release()

    def retrieveoutputs(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        itemmap = lockerinstance[0].SICKGMOD0['outputmap']
        lockerinstance[0].lock.release()
        for item in itemmap.items():
            positionInDatablock = item[0].split('.')
            address = 8*int(re.findall(r'\d+',positionInDatablock[0])[0])+int(re.findall(r'\d+',positionInDatablock[1])[0])
            try:
                self.write_coil(address, item[1])
            except Exception as e:
                errstring = "\nGMOD error - can't retrieve outputs " + str(e)
                ErrorEventWrite(lockerinstance, errstring)

    def safetysignals(self, lockerinstance):
        for binding in [self.parameters['inputbinding'],self.parameters['outputbinding']]:
            src = binding['sourcemasterkey']
            dst = binding['destinymasterkey']
            for item in binding.items():
                if item[1] in [src, dst]:
                    continue
                if src == 'safety':
                    lockerinstance[0].lock.acquire()
                    signal = dictKeyByVal(lockerinstance[0].shared[dst]['outputs'],item[1])
                    lockerinstance[0].shared[dst]['outputmap'][signal] = lockerinstance[0].shared[src][item[0]]
                    lockerinstance[0].lock.release()
                else:
                    lockerinstance[0].lock.acquire()
                    signal = dictKeyByVal(lockerinstance[0].shared[src]['inputs'],item[0])
                    lockerinstance[0].shared[dst][item[1]] = lockerinstance[0].shared[src]['inputmap'][signal]
                    lockerinstance[0].lock.release()
