from Sources import ErrorEventWrite, dictKeyByVal, Bits
import json
import csv
import re
from .common import EventManager
from xml.etree.ElementTree import ElementTree as ET
from pymodbus.version import version
from pymodbus.server.sync import ModbusTcpServer, StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSparseDataBlock, ModbusSlaveContext, ModbusServerContext
from threading import Thread, _active
from pymodbus.transaction import ModbusSocketFramer
DEBUG = False
#DEBUG = True
if DEBUG:
    import logging
    logging.basicConfig()
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

class FX0GMOD(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datablocks = {
            'ReqInputDataset1':(400001,('list',(25,)),'r'),
            'ReqInputDataset2':(400100,('list',(16,)),'r'),
            'ReqInputDataset3':(400200,('list',(30,)),'r'),
            'ReqInputDataset4':(400300,('list',(30,)),'r'),
            'WriteOutputDataset1':(401000,('list',(5,)),'w'),
            'WriteOutputDataset2':(401100,('list',(5,)),'w'),
            'WriteOutputDataset3':(401200,('list',(5,)),'w'),
            'WriteOutputDataset4':(401300,('list',(5,)),'w'),
            'WriteOutputDataset5':(401400,('list',(5,)),'w')}

class SICKGmod(FX0GMOD):
    def __init__(self, lockerinstance, datablock = None):
        FX0GMOD.__init__(self)
        self.datablock = datablock
        self.lockerinstance = lockerinstance
        self.Bits = Bits(len = 16)

    def read_coils(self, address, amount = 1):
        startword = address//16
        endword = (address+amount)//16
        startbit = address%16
        endbit = (address+amount)%16
        result = []
        for word, readword in enumerate(self.datablock.getValues(startword, endword-startword+1),startword):
            for i, bit in enumerate(self.Bits(readword)):
                if word == startword:
                    if i < startbit: continue
                if word == endword:
                    if i >= endbit: break
                result.append(bit)
        return result

    def write_coil(self, address, value):
        word = address//16
        bit = address%16
        for i in range(16):
            if bit >> i:
                continue
            else:
                bit = i
                break
        readword = self.Bits(self.datablock.getValues(word))
        writeword = (~(0b1<<bit)&readword)|(value<<bit)
        # 0b1<<bit - binary position for bit to write
        # ~(0b1<<bit) - negated position represents bitmask for every other bits
        # ~(0b1<<bit)&readbyte - whole value except one bit to write
        # (value<<bit) - bit to write on position (0 if False) 
        # (~(0b1<<bit)&readbyte)|(value<<bit) - write bit to it's position
        self.datablock.setValues(word, self.Bits(writeword))

class ModbusTcpServerExternallyTerminated(ModbusTcpServer):
    def __init__(self, context, framer=None, identity=None,
                 address=None, handler=None, allow_reuse_address=False,
                 **kwargs):
        if 'lockerinstance' in kwargs.keys():
            self.lockerinstance = kwargs.pop('lockerinstance')
            EventManager.AdaptEvent(self.lockerinstance, input = 'events.closeApplication', callback = super().shutdown)
        super().__init__(self, context, **kwargs)

def StartTcpServerExternallyTerminated(context=None, identity=None, address=None,
                   custom_functions=[], **kwargs):
    framer = kwargs.pop("framer", ModbusSocketFramer)
    server = ModbusTcpServerExternallyTerminated(context, framer, identity, address, **kwargs)
    for f in custom_functions:
        server.decoder.register(f)
    server.serve_forever()

class ModbusServerForGMOD():
    def __init__(self, lockerinstance, configfile):
        with open(configfile, 'r') as jsonfile:
            self.config = json.load(jsonfile)['server']
        identity = ModbusDeviceIdentification()
        identity.VendorName = self.config['vendorname']#"AIC MW"
        identity.ProductCode = self.config['productcode']#'HMI'
        identity.ProductName = self.config['productname']#'Cela spawania lsterkowego'
        self.datablock = ModbusSparseDataBlock({addr:0 for addr in range(self.config['startaddress'],self.config['endaddress'],1)}) 
        store = ModbusSlaveContext(hr = self.datablock)
        context = ModbusServerContext(slaves = {0x01:store}, single=False)
        TCPServerargs= { 'lockerinstance':lockerinstance,
                         'context':context,
                         'identity':identity,
                         'address':('',self.config['port'])}
        self.thread = Thread(target = StartTcpServerExternallyTerminated, kwargs = TCPServerargs)
        self.thread.start()

class GMOD(SICKGmod):
    def __init__(self, lockerinstance, configFile, *args, **kwargs): #configFile must have path to csv generated in FlexiSoft Designer
        self.lockerinstance = lockerinstance
        while True:
            try:
                with open(configFile, 'r') as jsonfile:
                    self.parameters = json.load(jsonfile)
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
                    self.datainputoffset = self.parameters['datablocksOffset']['InputDataset1']
                    self.dataoutputoffset = self.parameters['datablocksOffset']['OutputDataset1']
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
                                    with lockerinstance[0].lock:
                                        lockerinstance[0].SICKGMOD0['inputs'][entry[0]] = entry[1]
                                        lockerinstance[0].SICKGMOD0['inputmap'][entry[0]] = False
                        for entry in self.outputs:
                            entry = entry[0].split(';')
                            if len(entry)>1:
                                if entry[1] and '.' in entry[0]:
                                    with lockerinstance[0].lock:
                                        lockerinstance[0].SICKGMOD0['outputs'][entry[0]] = entry[1]
                                        lockerinstance[0].SICKGMOD0['outputmap'][entry[0]] = False
                    except Exception as e:
                        errstring = '\nGMOD init error - extending DictProxy failed ' + str(e)
                        ErrorEventWrite(lockerinstance, errstring)
                    else:
                        try:
                            self.server =  ModbusServerForGMOD(lockerinstance, configFile)
                            SICKGmod.__init__(self, lockerinstance, self.server.datablock)
                            self.Alive = True
                            with lockerinstance[0].lock:
                                lockerinstance[0].SICKGMOD0['Alive'] = True
                        except Exception as e:
                            errstring = 'GMOD error ' + str(e)
                            ErrorEventWrite(lockerinstance, errstring)
                        else:
                            self.Bits = Bits(len=16)
                            self.loop(lockerinstance)
            with lockerinstance[0].lock:
                letdie = not lockerinstance[0].SICKGMOD0['Alive']
                letdie |= lockerinstance[0].events['closeApplication']
            if letdie: break
    
    def loop(self, lockerinstance):
        while self.Alive:
            self.retrieveinputs(lockerinstance)
            self.retrieveoutputs(lockerinstance)
            self.safetysignals(lockerinstance)
            with lockerinstance[0].lock:
                self.Alive = lockerinstance[0].SICKGMOD0['Alive'] and not lockerinstance[0].events['closeApplication']

    def retrieveinputs(self, lockerinstance):
        with lockerinstance[0].lock:
            itemmap = lockerinstance[0].shared['SICKGMOD0']['inputmap'].keys()
        for item in itemmap:
            positionInDatablock = item.split('.')
            byte = re.findall(r'\d+',positionInDatablock[0])[0]
            bit = re.findall(r'\d+',positionInDatablock[1])[0]
            offset = self.datainputoffset * 16
            address = 8*int(byte)+int(bit)+offset
            try:
                receive = self.read_coils(address)
                if receive:
                    result = receive[0]
                else: result = False
            except Exception as e:
                errstring = "\nGMOD error - can't retrieve inputs " + str(e)
                ErrorEventWrite(lockerinstance, errstring)
            else:
                with lockerinstance[0].lock:
                    lockerinstance[0].SICKGMOD0['inputmap'][item] = result

    def retrieveoutputs(self, lockerinstance):
        with lockerinstance[0].lock:
            itemmap = lockerinstance[0].shared['SICKGMOD0']['outputmap']
        for item in itemmap.items():
            positionInDatablock = item[0].split('.')
            address = 8*int(re.findall(r'\d+',positionInDatablock[0])[0])+int(re.findall(r'\d+',positionInDatablock[1])[0])
            try:
                self.write_coil(address + self.dataoutputoffset*16, item[1])
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
                    with lockerinstance[0].lock:
                        outputs = lockerinstance[0].shared[dst]['outputs']
                    signal = dictKeyByVal(outputs,item[1])
                    with lockerinstance[0].lock:
                        lockerinstance[0].shared[dst]['outputmap'][signal] = lockerinstance[0].shared[src][item[0]]
                else:
                    with lockerinstance[0].lock:
                        inputs = lockerinstance[0].shared[src]['inputs']
                    signal = dictKeyByVal(inputs,item[0])
                    with lockerinstance[0].lock:
                        byte = lockerinstance[0].shared[src]['inputmap'][signal]
                        lockerinstance[0].shared[dst][item[1]] = byte
