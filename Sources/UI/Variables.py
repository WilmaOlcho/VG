
INT = type(1)
STRING = type('')
MENU = "MENU"

class Variables(dict):
    def __init__(self, lockerinstance, **widgetsettings):
        self.lockerinstance = lockerinstance
        self['widgetsettings'] = widgetsettings
        self.jsonpath = ''
        self.currentProgram = ''
        self.currentProgramIndex = 0
        self.programposstart = 0
        self.programposend = 1
        self.programcolumns = ["ID","Kolejność","Program SCOUT","Warstwa SCOUT","Pozycja robota","Tabela pozycji","Pozycja serwo","reserved","reserved"]
        self.displayedprogramcolumns = [False,True,True,True,True,True,True,False,False]
        self.columnwidths = [4,10,30,15,14,14,17,15,15]
        self.columntypes = [INT, INT, MENU, INT, INT, INT, INT, INT, INT]
        self.internalEvents = {
            'ProgramMenuRefresh':False,
            'RefreshStartEnd':False,
            'TableRefresh':False,
            'DumpProgramToFile':False,
            'ack' : False,
            'error': True,
            'start':False,
            'stop':False,
            'buttonclicked':False
        }

        self['statusindicators'] = {
            'Safety':-1,
            'ShieldingGas':False,
            'VacuumFilter':False,
            'Air':True,
            'Crossjet':False,
            'Light':False,
            'Troley':False,
            'Robot':False
        }
        self.displayedprogramtableheight = 1000

        self['auto'] = False
        self['processtime'] = '0'
        self['currentposition'] = '0'
        self['progress'] = 0
        self['ProgramActive'] = False
        self['step'] = 0
        self['receipt'] = ''
        self['page'] = ''

        self['ImportantMessages'] = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
        self['troley'] = {
            'servoON':False,
            'servoRUN':False,
            'servoSTOP':False,
            'servoCOIN':False,
            'servoREADY':False,
            'servoSTEP':False,
            'servoHOMING':False,
            'servoRESET':False,
            'servoTGON':False,
            'TroleyDocked':False
        }
        self['robot'] = {
            'RobotGo':False,
            'RobotHoming':False,
            'table':0,
            'position':0,
            'actualposition':0,
            'RobotCommandActive':False,
            'RobotIsHome':False,
            'RobotInAPosition':False,
            'RobotHandMode':False,
            'RobotMotorsOn':False,
            'RobotCycle':False,
            'ConnectionActive':False
        }
        self['laser'] = {
            'LaserOn':False,
            'LaserTurnOn':False,
            'LaserTurnOff':False,
            'LaserIsOn':False,
            'GetChannel':False,
            'ReleaseChannel':False,
            'ResetErrors':False,
            'LaserReady':False,
            'LaserAssigned':False,
            'LaserError':False,
            'LaserWarning':False,
            'ChillerError':False,
            'ChillerWarning':False,
            'LaserBusy':False
        }
        self['safety'] = {
            'EstopArmed':False,
            'DoorLocked':False,
            'TroleyInside':False,
            'THCPushed':False,
            'RobotTeachMode':False,
            'DeadMan':False,
            'ZoneArmed':False,
            'Estopresetrecquired':False,
            'Zoneresetrecquired':False,
            'OpenTheDoor':False
        }
        self['scout'] = {
            'WaitingForData':False,
            'ready':False,
            'atstart':False,
            'alarm':False,
            'NA':False,
            'progress':False,
            'laseron':False,
            'wobble':False,
            'connection':False,
            'align':False,
            "weld":False,
            'getaligninfo':False,
            'showaligninfo':False,
            'versionvariable':"",
            'setreceipt':False,
            'alarmreset':False,
            'receipt':"",
            'setpage':False,
            "page":0,
            "pagecheck":0,
            'AlignInfoA':0.0,
            'AlignInfoX':0.0,
            'AlignInfoY':0.0,
            'recipes':[],
            "bAtstart":False,
            "bAtstop":False,
            "bLaserCTRL":False
        }
        self['pistoncontrol'] = {
            'seal':{
                'Left':{
                    'coil':False,
                    'sensor':False},
                'Center':{},
                'Right':{
                    'coil':False}
            },
            'shieldinggas':{
                'Right':{
                    'coil':False
                },
                'Center':{
                    'sensor':False
                }
            },
            'crossjet':{
                'Right':{
                    'coil':False},
                'Center':{
                    'sensor':False
                }
            },
            'headcooling':{
                'Right':{
                    'coil':False},
                'Center':{
                    'sensor':False
                }
            },
            'pusher':{
                'Left':{
                    'coil':False,
                    'sensor':False},
                'Right':{
                    'coil':False,
                    'sensor':False},
                'Center':{}
            }
        }
        self.Alive = True

    def update(self):
        lockerinstance = self.lockerinstance
        if True:
            if isinstance(self['scout']['page'], str):
                if self['scout']['page'].isnumeric():
                    self['scout']['page'] = int(self['scout']['page'])
                else:
                    self['scout']['page'] = 0
            with lockerinstance[0].lock:
                pneumatics = lockerinstance[0].pistons
                robot = lockerinstance[0].robot
                safety = lockerinstance[0].safety
                troley = lockerinstance[0].troley
                laser = lockerinstance[0].lcon
                multiplexer = lockerinstance[0].mux
                servo = lockerinstance[0].servo
                events = lockerinstance[0].events
                program = lockerinstance[0].program
                scout = lockerinstance[0].scout
                if self.internalEvents['buttonclicked']:
                    self.internalEvents['buttonclicked'] = False
                    lockerinstance[0].GPIO['somethingChanged'] = True

                self['safety']['EstopArmed'] = safety['EstopArmed']
                self['safety']['DoorLocked'] = safety['DoorLocked']
                self['safety']['TroleyInside'] = safety['TroleyInside']
                self['safety']['THCPushed'] = safety['THCPushed']
                self['safety']['RobotTeachMode'] = safety['RobotTeachMode']
                self['safety']['DeadMan'] = safety['DeadMan']
                self['safety']['ZoneArmed'] = safety['ZoneArmed']
                self['safety']['Estopresetrecquired'] = safety['Estopresetrecquired']
                self['safety']['Zoneresetrecquired'] = safety['Zoneresetrecquired']

                self['pistoncontrol']['seal']['Left']['sensor'] = pneumatics['sensorSealDown']
                self['pistoncontrol']['pusher']['Left']['sensor'] = pneumatics['sensorTroleyPusherBack']
                self['pistoncontrol']['pusher']['Right']['sensor'] = pneumatics['sensorTroleyPusherFront']
                self['pistoncontrol']['shieldinggas']['Center']['sensor'] = pneumatics['ShieldingGas']
                self['pistoncontrol']['crossjet']['Center']['sensor'] = pneumatics['sensorVacuumOk']
                self['pistoncontrol']['headcooling']['Center']['sensor'] = pneumatics['sensorAirOk']
                self['laser']['LaserIsOn'] = laser['LaserOn']
                self['laser']['LaserBusy'] = multiplexer['busy']
                self['laser']['LaserReady'] = laser['LaserReady']
                self['laser']['LaserError'] = laser['LaserError']
                self['laser']['LaserWarning'] = laser['LaserWarning']
                self['laser']['ChillerError'] = laser['ChillerError']
                self['laser']['ChillerWarning'] = laser['ChillerWarning']
                self['troley']['servoON'] = servo['active']
                self['troley']['servoCOIN'] = servo['iocoin']
                self['troley']['servoREADY'] = servo['ioready']
                self['troley']['servoTGON'] = servo['iotgon']
                self['troley']['TroleyDocked'] = troley['docked']        
                self.internalEvents['error'] = events['Error']
                self['ImportantMessages'] = lockerinstance[0].shared['Errors']
                self.alive = lockerinstance[0].console['Alive']
                program['startpos'] = self.programposstart
                program['endpos'] = self.programposend
                program['ProgramName'] = self.currentProgram
                program['ProgramsFilePath'] = self.jsonpath
                program['stepmode'] = not self['auto']
                program['automode'] = self['auto']
                program['running'] = self['ProgramActive']
                self['scout']['recipes'] = list(program['recipes'])
                if self.internalEvents['ack']:
                    events['ack'] = True
                    self.internalEvents['ack'] = False
                if not self['ProgramActive']:
                #SCOUT gui binding
                    self['scout']['ready'] = scout['status']['ReadyOn']
                    self['scout']['atstart'] = scout['status']['AutoStart']
                    self['scout']['alarm'] = scout['status']['Alarm']
                    self['scout']['NA'] = scout['status']['rsv']
                    self['scout']['progress'] = scout['status']['WeldingProgress']
                    self['scout']['laseron'] = scout['status']['LaserIsOn']
                    self['scout']['wobble'] = scout['status']['Wobble']
                    self['scout']['connection'] = scout['StatusCheckCode']
                    if scout['version']:
                        self['scout']['versionvariable'] = scout['version']
                    else:
                        scout['GetVersion'] |= True
                    if self['scout']['setpage']:
                        scout['ManualAlignPage'] = self['scout']['page']
                        scout['ManualWeldPage'] = self['scout']['page']
                        print('Manualpage {}'.format(scout['ManualAlignPage']))
                        self['scout']['setpage'] = False
                    else:
                        self['scout']['page'] = scout['ManualAlignPage']
                    if self['scout']['setreceipt']:
                        scout['recipe'] = self['scout']['receipt']
                        scout['SetRecipe'] |= True
                        self['scout']['setreceipt'] = False
                    else:
                        self['scout']['receipt'] = scout['recipe']
                        self['receipt'] = scout['recipe']
                    scout['ManualAlign'] |= self['scout']['align']
                    self['scout']['WaitingForData'] = scout['WaitingForData']
                    scout['ManualWeld'] |= self['scout']['weld']
                    scout['AlarmReset'] |= self['scout']['alarmreset']
                    scout['GetAlignInfo'] |= self['scout']['getaligninfo']
                    scout['AutostartOn'] |= self['scout']['bAtstart']
                    scout['AutostartOff'] |= self['scout']['bAtstop']
                    scout['LaserCTRL'] = not scout['LaserCTRL'] if self['scout']["bLaserCTRL"] else scout['LaserCTRL']
                    if scout['AlignInfoReceived']:
                        self['scout']['AlignInfoA'] = float('{}.{}'.format(scout['AlignInfo']['A'],scout['AlignInfo']['dotA']))
                        self['scout']['AlignInfoX'] = float('{}.{}'.format(scout['AlignInfo']['X'],scout['AlignInfo']['dotX']))
                        self['scout']['AlignInfoY'] = float('{}.{}'.format(scout['AlignInfo']['Y'],scout['AlignInfo']['dotY']))
                        self['scout']['showaligninfo'] = True
                        scout['AlignInfoReceived'] = False

                #releasing laser and opening the door when 'open the door' button is pushed
                    if self['safety']['OpenTheDoor']:
                        if laser['LaserReady']:
                            laser['ReleaseChannel'] = True
                        else:
                            safety['OpenTheDoor'] = True
                        if safety['OpenTheDoorAck']:
                            self['safety']['OpenTheDoor'] = False
                            safety['OpenTheDoor'] = False

                #Pneumatics GUI binding
                    pneumatics['TroleyPusherFront'] = self['pistoncontrol']['pusher']['Right']['coil']
                    pneumatics['TroleyPusherBack'] = self['pistoncontrol']['pusher']['Left']['coil']
                    pneumatics['SealUp'] = self['pistoncontrol']['seal']['Right']['coil']
                    pneumatics['SealDown'] = self['pistoncontrol']['seal']['Left']['coil']
                    pneumatics['ShieldingGas'] = self['pistoncontrol']['shieldinggas']['Right']['coil']
                    pneumatics['HeadCooling'] = self['pistoncontrol']['headcooling']['Right']['coil']
                    pneumatics['CrossJet'] = self['pistoncontrol']['crossjet']['Right']['coil']
                #Servo GUI binding
                    servo['homing'] |= self['troley']['servoHOMING']
                    servo['run'] |= self['troley']['servoRUN']
                    servo['stop'] |= self['troley']['servoSTOP']
                    servo['reset'] |= self['troley']['servoRESET']
                    servo['step'] |= self['troley']['servoSTEP']
                #Laser GUI binding
                    laser['SetChannel'] |= self['laser']['GetChannel'] #Here are the issues
                    multiplexer['acquire'] |= self['laser']['GetChannel']
                    laser['ReleaseChannel'] |= self['laser']['ReleaseChannel'] #Here are the issues
                    multiplexer['release'] |= self['laser']['ReleaseChannel']
                    laser['LaserTurnOn'] |= self['laser']['LaserTurnOn']
                    laser['LaserTurnOff'] |= self['laser']['LaserTurnOff']
                    laser['LaserReset'] |= self['laser']['ResetErrors']
                #robot GUI binding
                    robot['go'] |= self['robot']['RobotGo']
                    robot['homing'] |= self['robot']['RobotHoming']
                    robot['settable'] = self['robot']['table']
                    robot['setpos'] = self['robot']['position']
                #resetting variables after changes
                    self['laser']['LaserTurnOn'] = False
                    self['laser']['LaserTurnOff'] = False
                    self['laser']['GetChannel'] = False
                    self['laser']['ReleaseChannel'] = False
                    self['laser']['ResetErrors'] = False
                    self['robot']['RobotGo'] = False
                    self['robot']['RobotHoming'] = False
                    self['troley']['servoRUN'] = False
                    self['troley']['servoSTOP'] = False
                    self['troley']['servoHOMING'] = False
                    self['troley']['servoSTEP'] = False
                    self['troley']['servoRESET'] = False
                    self['scout']['align'] = False
                    self['scout']['weld'] = False
                    self['scout']['alarmreset'] = False
                    self['scout']['getaligninfo'] = False
                    self['scout']['bAtstart'] = False
                    self['scout']['bAtstop'] = False
                    self['scout']["bLaserCTRL"] = False

                else:
                    print(program['recipes'])
                    self['currentposition'] = 'wiersz {}, krok {}'.format(program['cycle'], program['stepnumber'])
                    self['processtime'] = str(program['time'])
                    self['progress'] = str(program['cycle'])
                    self['step'] = str(program['stepnumber'])
                #status
                #pneumatics
                if pneumatics['ShieldingGas'] and pneumatics['sensorShieldingGasOk']:
                    self['statusindicators']['ShieldingGas'] = 1
                elif pneumatics['ShieldingGas'] and not pneumatics['sensorShieldingGasOk']:
                    self['statusindicators']['ShieldingGas'] = -1
                else:
                    self['statusindicators']['ShieldingGas'] = 0
                if pneumatics['CrossJet'] and pneumatics['sensorAirOk']:
                    self['statusindicators']['Crossjet'] = 1
                elif pneumatics['CrossJet'] and not pneumatics['sensorAirOk']:
                    self['statusindicators']['Crossjet'] = -1
                else:
                    self['statusindicators']['Crossjet'] = 0
                if pneumatics['sensorAirOk']:
                    self['statusindicators']['Air'] = 1
                else:
                    self['statusindicators']['Air'] = 0
                if pneumatics['sensorVacuumOk']:
                    self['statusindicators']['VacuumFilter'] = 1
                else:
                    self['statusindicators']['VacuumFilter'] = 0
                self['statusindicators']['Light'] = 1
                #troley
                if troley['docked'] and not troley['error']:
                    self['statusindicators']['Troley'] = 1
                elif troley['error'] or not troley['Alive']:
                    self['statusindicators']['Troley'] = -1
                else:
                    self['statusindicators']['Troley'] = 0
                #robot
                if robot['Alive'] and not robot['error']:
                    self['statusindicators']['Robot'] = 1
                    self['robot']['actualposition'] = robot['currentpos']
                    self['robot']['RobotCommandActive'] = robot['activecommand']
                    self['robot']['RobotIsHome'] = robot['homepos']
                    self['robot']['RobotInAPosition'] = robot['currentpos'] == robot['setpos']
                    self['robot']['RobotHandMode'] = robot['handmode']
                    self['robot']['RobotMotorsOn'] = robot['motors']
                    self['robot']['RobotCycle'] = robot['cycle']
                    self['robot']['ConnectionActive'] = robot['connection']

                elif robot['error'] or not robot['Alive']:
                    self['statusindicators']['Robot'] = -1
                else:
                    self['statusindicators']['Robot'] = 0
                #safety
                if safety['EstopArmed'] and safety['ZoneArmed']:
                    self['statusindicators']['Safety'] = 1
                elif not safety['EstopArmed']:
                    self['statusindicators']['Safety'] = -1
                elif safety['Estopresetrecquired'] or safety['Zoneresetrecquired']:
                    self['statusindicators']['Safety'] = -2
                else:
                    self['statusindicators']['Safety'] = 0
