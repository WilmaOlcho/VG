from multiprocessing import Manager, Lock, Array, Value

class SharedLocker(object):
    def __init__(self, *args, **kwargs):
        manager = Manager()
        self.inputs = Array('b',32*[False])
        self.outputs = Array('b',32*[False])
#        self.GPIO = {
#            'I1': self.inputs[0], 'I2': self.inputs[1], 'I3': self.inputs[2], 'I4': self.inputs[3],
#            'I5': self.inputs[4], 'I6': self.inputs[5], 'I7': self.inputs[6], 'I8': self.inputs[7],
#            'I9': self.inputs[8], 'I10': self.inputs[9], 'I11': self.inputs[10], 'I12': self.inputs[11],
#            'I13': self.inputs[12], 'I14': self.inputs[13], 'I15': self.inputs[14], 'I16': self.inputs[15],
#            'I17': self.inputs[16], 'I18': self.inputs[17], 'I19': self.inputs[18], 'I20': self.inputs[19],
#            'I21': self.inputs[20], 'I22': self.inputs[21], 'I23': self.inputs[22], 'I24': self.inputs[23],
#            'I25': self.inputs[24], 'I26': self.inputs[25], 'I27': self.inputs[26], 'I28': self.inputs[27],
#            'I29': self.inputs[28], 'I30': self.inputs[29], 'I31': self.inputs[30], 'I32': self.inputs[31],
#            'O1': self.outputs[0], 'O2': self.outputs[1], 'O3': self.outputs[2], 'O4': self.outputs[3],
#            'O5': self.outputs[4], 'O6': self.outputs[5], 'O7': self.outputs[6], 'O8': self.outputs[7],
#            'O9': self.outputs[8], 'O10': self.outputs[9], 'O11': self.outputs[10], 'O12': self.outputs[11],
#            'O13': self.outputs[12], 'O14': self.outputs[13], 'O15': self.outputs[14], 'O16': self.outputs[15],
#            'O17': self.outputs[16], 'O18': self.outputs[17], 'O19': self.outputs[18], 'O20': self.outputs[19],
#            'O21': self.outputs[20], 'O22': self.outputs[21], 'O23': self.outputs[22], 'O24': self.outputs[23],
#            'O25': self.outputs[24], 'O26': self.outputs[25], 'O27': self.outputs[26], 'O28': self.outputs[27],
#            'O29': self.outputs[28], 'O30': self.outputs[29], 'O31': self.outputs[30], 'O32': self.outputs[31]}
        self.shared = manager.dict({
            'SCOUT':manager.dict({
                'Alive':False,
                'connectionbuffer':b'',
                'LastMessageType':"",
                'status':manager.dict({
                    'ReadyOn':False,
                    "AutoStart":False,
                    "Alarm":False,
                    "rsv":False,
                    "WeldingProgress":False,
                    "LaserIsOn":False,
                    "Wobble":False
                })
                }),
            'Errors':'',
            'servoModuleFirstAccess':True,
            'configurationError':False,
            'TactWDT':False,
            'wdt':manager.list(),
            'ect':manager.list(),
            'lcon':manager.dict({
                'Alive':False,
                'LaserTurnOn':False,
                'LaserTurnOff':False,
                "LaserReset":False,
                'SetChannel':False,
                'LaserError':False,
                'LaserWarning':False,
                'ChillerError':False,
                'ChillerWarning':False,
                'LaserReady':False,
                'LaserOn':False,
                'LaserAssigned':False
                }),
            'events':manager.dict({
                'KDrawMessageReceived':False,
                'startprogram':False,
                'somethingchanged':False,
                'ack':False,
                'erroracknowledge':False,
                'Error':False,
                'stepComplete':False,
                'RobotHomingComplete':False,
                'RobotGoComplete':False,
                'RobotSetoffsetComplete':False,
                'RobotGoonceComplete':False,
                'RobotMoving':True,
                'ServoMoving':False,
                'anyButtonPressed':False,
                'ServoResetDone':False,
                'ServoHomingComplete':False,
                'ServoStepComplete':False,
                'closeApplication':False,
                'OutputChangedByRobot':False,
                'OutputsChangedByRobot':''}),
            'pistons':manager.dict({
                'Alive':False,
                'SealUp':False,
                'SealDown':False,
                'sensorSealUp':True,
                'sensorSealDown':False,
                'sensorTroleyPusher2Front':False,
                'sensorTroleyPusher2Back':False,
                'TroleyPusherFront':False,
                'TroleyPusherBack':False,
                'sensorTroleyPusherFront':False,
                'sensorTroleyPusherBack':False,
                'sensorShieldingGasOk':False,
                'sensorAirOk':False,
                'sensorVacuumOk':True,
                'ShieldingGas':False,
                'HeadCooling':False,
                'CrossJet':False}),
            'safety':manager.dict({
                'EstopArmed':False,
                'DoorOpen':False,
                'DoorClosed':False,
                'DoorLocked':False,
                'TroleyInside':False,
                'THCPushed':False,
                'RobotError':False,
                'RobotTeachMode':False,
                'DeadMan':False,
                'LaserError':False,
                'ServoError':False,
                'sValve1Error':False,
                'ServoEDM':False,
                'sValve1EDM':False,
                'RobotEDM':False,
                'LaserEDM':False,
                'ZoneArmed':False,
                'ZoneError':False,
                'TroleyReady':False,
                "resetbutton":False,
                "Estopresetrecquired":False,
                "Zoneresetrecquired":False}),
            'mux':manager.dict({
                'busy':False,
                'ready':False,
                'onpath':False,
                'acquire':False,
                'release':False,
                'Alive':False,
                'Channel':-1}),
            'servo':manager.dict({
                'Alive':False,
                'homing':False,
                'step':False,
                'reset':False,
                'run':False,
                'stop':False,
                'positionNumber':-1,
                'moving':False,
                'active':False,
                'iocoin':False,  #bint it to servo control signals
                'ioready':False, #
                'iotgon':False   #
                }),
            'troley':manager.dict({
                'Alive':False,
                'docked':False,
                'number':0,
                'dockreleaseswitch':False,
                'error':False,
                'push':False,
                'dock':False,
                'undock':False,
                'rotate':False
                }),
            'robot':manager.dict({
                'CommandControl':True,
                'PositionControl':True,
                'Alive':False,
                'error':False,
                'homepos':False,
                'homing':False,
                'go':False,
                'setoffset':False,
                'goonce':False,
                'handmode':False,
                'motors':False,
                'cycle':False,
                'connection':False,
                'settable':0,
                'setpos':0,
                'currentpos':0,
                'activecommand':False,
                'A':0.0,
                'X':0.0,
                'Y':0.0,
                'Z':0.0,
                'StatusRegister0':0,
                'StatusRegister1':0,
                'StatusRegister2':0,
                'StatusRegister3':0,
                'StatusRegister4':0,
                'StatusRegister5':0,
                'StatusRegister6':0}),
            'console':manager.dict({
                'Alive':False}),
            'GPIO':manager.dict({
                'somethingChanged':False,
                'I1':False, 'I2':False, 'I3':False, 'I4':False,
                'I5':False, 'I6':False, 'I7':False, 'I8':False,
                'I9':False, 'I10':False, 'I11':False, 'I12':False,
                'I13':False, 'I14':False, 'I15':False, 'I16':False,
                'I17':False, 'I18':False, 'I19':False, 'I20':False,
                'I21':False, 'I22':False, 'I23':False, 'I24':False,
                'I25':False, 'I26':False, 'I27':False, 'I28':False,
                'I29':False, 'I30':False, 'I31':False, 'I32':False,
                'O1':False, 'O2':False, 'O3':False, 'O4':False,
                'O5':False, 'O6':False, 'O7':False, 'O8':False,
                'O9':False, 'O10':False, 'O11':False, 'O12':False,
                'O13':False, 'O14':False, 'O15':False, 'O16':False,
                'O17':False, 'O18':False, 'O19':False, 'O20':False,
                'O21':False, 'O22':False, 'O23':False, 'O24':False,
                'O25':False, 'O26':False, 'O27':False, 'O28':False,
                'O29':False, 'O30':False, 'O31':False, 'O32':False}),
            'SICKGMOD0':manager.dict({
                'Alive':False,
                'inputs':manager.dict({}), 
                'outputs':manager.dict({}),
                'inputmap':manager.dict({}),
                'outputmap':manager.dict({})
                }),
            'program':manager.dict({
                'Alive':False,
                'stepmode':False,
                'stepcomplete':False,
                'initialising':False,
                'automode':False,
                'running':False,
                '/running':True,
                'programname':'',
                'stepnumber':0,
                'cycle':0
                })
                })
        self.scout = self.shared['SCOUT']
        self.program = self.shared['program']
        self.wdt = self.shared['wdt']
        self.troley = self.shared['troley']
        self.ect = self.shared['ect']
        self.lcon = self.shared['lcon'] 
        self.lock = Lock()
        self.attempts = Value('i',4)
        self.events = self.shared['events'] 
        self.errorlevel = Array('b',256*[False])
        self.pistons = self.shared['pistons'] 
        self.safety = self.shared['safety'] 
        self.mux = self.shared['mux']
        self.servo = self.shared['servo']
        self.robot = self.shared['robot']
        self.console = self.shared['console']
        self.GPIO = self.shared['GPIO']
        self.SICKGMOD0 = self.shared['SICKGMOD0']

if __name__=='__main__':
    lck = SharedLocker()
    with lck.lock:
        print(lck.events['Error'])
    with lck.lock:
        lck.events['Error'] = True
    with lck.lock:
        print(lck.events['Error'])