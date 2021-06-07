from multiprocessing import Manager, Lock, Array, Value

class SharedLocker(object):
    def __init__(self, *args, **kwargs):
        mainpath = kwargs.pop('mainpath','.\\')
        manager = Manager()
        self.inputs = Array('b',32*[False])
        self.outputs = Array('b',32*[False])
        self.shared = manager.dict({
            'main':manager.dict({
                'Window':True,
                'MyMultiplexer':True,
                'Servo':True,
                'MyLaserControl':True,
                'RobotVG':True,
                'PneumaticsVG':True,
                'GMOD':True,
                'Troley':True,
                'Program':True,
                'SCOUT':True,
                'RobotPlyty':True
            }),
            'paramfiles':manager.dict({
                'Window':(mainpath + 'widgetsettings.json', mainpath + 'Programs.json',),
                'MyMultiplexer':(mainpath + 'amuxConfiguration.json',),
                'Servo':(mainpath + 'ServoSettings.json',),
                'MyLaserControl':(mainpath + 'amuxConfiguration.json',),
                'RobotVG':(mainpath + 'robotConfiguration.json',),
                'PneumaticsVG':(mainpath + 'PneumaticsConfiguration.json',),
                'GMOD':(mainpath + 'SICKGMODconfiguration.json',),
                'Troley':(mainpath + 'Troleysettings.json',),
                'Program':(mainpath + 'Programs.json',),
                'RobotPlyty':(mainpath + 'robot2Configuration.json',),
                'SCOUT':(mainpath + 'Scoutconfiguration.json',)
            }),
            'SCOUT':manager.dict({
                'Alive':False,
                'WaitingForData':False,
                'connectionbuffer':b'',
                'LastMessageType':manager.list(['','','','']),
                'actualmessage':b'',
                'MessageAck':False,
                'version':'',
                'recipe':'test',
                'lastrecipe':'test',
                'recipesdir':'',
                'pagesToWeld':manager.list([]),
                'weldrunpagescount':0,
                'LaserOn':False,
                'ManualAlignPage':0,
                'ManualAlignCheck':False,
                'ManualWeldPage':0,
                'ManualWeldCheck':False,
                'StatusCheckCode':False,
                'AlignInfo':manager.dict({
                    '0':0,
                    '1':0,
                    '2':0,
                    "A":0,
                    "dotA":0,
                    "X":0,
                    "dotX":0,
                    "Y":0,
                    "dotY":0,
                }),
                'status':manager.dict({
                    'ReadyOn':False,
                    "AutoStart":False,
                    "Alarm":False,
                    "rsv":False,
                    "WeldingProgress":False,
                    "LaserIsOn":False,
                    "Wobble":False
                }),
                'scanwobble':manager.dict({
                    'mode':0,
                    "frequency":1,
                    "amplitude":0,
                    "power":0
                }),
                'times':manager.dict({
                    'setrecipe':0,
                    'limitsetrecipe':30,
                    'autostart':0,
                    'status':0
                }),
                'SetRecipe':False,
                'TurnLaserOn':False,
                'TurnLaserOff':False,
                'GetVersion':False,
                'AlarmReset':False,
                'AutostartOn':False,
                'AutostartOff':False,
                'ManualAlign':False,
                'ManualWeld':False,
                'WeldStart':False, #requires pages to weld list
                'Wobble':False,
                'GetAlignInfo':False,
                'AlignInfoReceived':False,
                'Recipechangedsuccesfully':False,
                'LaserCTRL':False,
                'LaserCTRVal':False

            }),
            'Errors':'',
            'Errcodes':manager.list(),
            'Statuscodes':manager.list(),
            "Steptime":0.0,
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
                'ReleaseChannel':False,
                'LaserError':False,
                'LaserWarning':False,
                'ChillerError':False,
                'ChillerWarning':False,
                'LaserReady':False,
                'LaserOn':False,
                'LaserAssigned':False,
                'InternalControlSet':False,
                'locklaserloop':False
                }),
            'events':manager.dict({
                'stopprogram':False,
                'ScoutManagerReadyToSend':False,
                'KDrawMessageReceived':False,
                'KDrawWaitingForMessage':False,
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
                'requestlconresettimer':False,
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
                'CrossJet':False,
                '':False}),
            'safety':manager.dict({
                'TroleyReadyForcedbyProgram':False,
                'EstopArmed':False,
                'TroleyDirection':False,
                'DoorOpen':False,
                "OpenTheDoorAck":False,
                'OpenTheDoor':False,
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
                'iocoin':False,
                'ioready':False,
                'iotgon':False
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
            'robot2':manager.dict({
                'Alive':False,
                'error':False,
                'Status':0,
                'Info':0,
                'Est_VG':0.0,
                'Est_PLYTY':0.0,
                'laserlocked':False}),
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
                'recipes':manager.list(),
                'ProgramsFilePath':'',
                'ProgramName':'',
                'Alive':False,
                'stepmode':False,
                'stepcomplete':False,
                'initialising':False,
                'initialised':False,
                'automode':False,
                'running':False,
                '/running':True,
                'stepnumber':0,
                'cycle':0, 
                'starttime':0.0,
                'currenttime':0.0,
                'time':0.0,
                'startpos':0,
                'endpos':0,
                'programline':manager.list([]),
                'cycleended':False,
                'handmodelaserrequire':False
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
        self.robot2 = self.shared['robot2']
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