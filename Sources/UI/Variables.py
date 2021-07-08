import re
INT = type(1)
STRING = type('')
MENU = "MENU"
PROMPTMENU = "PROMPTMENU"

class Variables(dict):
    def __init__(self, lockerinstance, **widgetsettings):
        self.lockerinstance = lockerinstance
        self['widgetsettings'] = widgetsettings
        self.jsonpath = ''
        self.currentProgram = ''
        self.currentProgramIndex = 0
        self.programposstart = 0
        self.programposend = 1
        self.programcolumns = ["ID","Kolejność","Program SCOUT","Warstwa SCOUT","Pozycja robota","Tabela pozycji","Pozycja serwo","Pilnuj lasera","reserved"]
        self.displayedprogramcolumns = [False,True,True,True,True,True,True,True,False]
        self.columnwidths = [4,10,30,15,14,14,17,17,15]
        self.columntypes = [INT, INT, MENU, INT, INT, INT, INT, PROMPTMENU, INT]
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
        self['servo'] = {
            'pos':-1
        }
        self['troley'] = {
            'homing':False,
            'step':False,
            'reset':False,
            'run':False,
            'stop':False,
            'positionNumber':0,
            'position':0,
            'moving':False,
            'active':False,
            'iocoin':False,
            'ioready':False,
            'iotgon':False,
            "notreadytoswitchon":False,
            "disabled":False,
            "readytoswitchon":False,
            "switchon":False,
            "operationenabled":False,
            "faultreactionactive":False,
            "fault":False,
            "warning":False,
            'positionreached':False,
            'TroleyDocked':False,
            'homepositionisknown':False,
            "homingattained":False
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
            'LaserBusy':False,
            'locklaserloop':False
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
            'OpenTheDoor':False,
            "TroleyReady":False,
            'ProgramTroleyRelease':False,
            'ProgramTroleyReleaseAcknowledged':False,
            "RobotEDM":False
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
            "bLaserCTRL":False,
            "bLaserCTRLHighlight":False
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

    def robotupdate(self):
        lock = self.lockerinstance[0].lock
        robot = self.lockerinstance[0].robot
        with lock:
            if not self['ProgramActive']:
                robot['go'] |= self['robot']['RobotGo']
                robot['homing'] |= self['robot']['RobotHoming']
                robot['settable'] = self['robot']['table']
                robot['setpos'] = self['robot']['position']
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
        self['robot']['RobotGo'] = False
        self['robot']['RobotHoming'] = False

    def troleyupdate(self):
        lock = self.lockerinstance[0].lock
        servo = self.lockerinstance[0].servo
        troley = self.lockerinstance[0].troley
        with lock:
            if not self['ProgramActive']:
                self['troley']['position'] != servo['positionNumber']
                servo['positionNumber'] = self['troley']['position']
                servo['homing'] |= self['troley']['homing']
                servo['run'] |= self['troley']['run']
                servo['stop'] |= self['troley']['stop']
                servo['reset'] |= self['troley']['reset']
                servo['step'] |= self['troley']['step']
            if troley['docked'] and not troley['error']:
                self['statusindicators']['Troley'] = 1
            elif troley['error'] or not troley['Alive']:
                self['statusindicators']['Troley'] = -1
            else:
                self['statusindicators']['Troley'] = 0
            self['troley']["homingattained"] = servo["homingattained"]
            self['troley']['readytoswitchon'] = servo['readytoswitchon']
            self['troley']['switchon'] = servo['switchon']
            self['troley']['operationenabled'] = servo['operationenabled']
            self['troley']['faultreactionactive'] = servo['faultreactionactive']
            self['troley']['fault'] = servo['fault']
            self['troley']['warning'] = servo['warning']
            self['troley']['positionreached'] = servo['positionreached']
            self['troley']['homepositionisknown'] = servo['homepositionisknown']
            self['troley']['TroleyDocked'] = troley['docked']
            self['servo']['pos'] = servo['positionNumber']
            
        self['troley']['run'] = False
        self['troley']['stop'] = False
        self['troley']['homing'] = False
        self['troley']['step'] = False
        self['troley']['reset'] = False

    def scoutupdate(self):
        lock = self.lockerinstance[0].lock
        scout = self.lockerinstance[0].scout
        laser = self.lockerinstance[0].lcon
        safety = self.lockerinstance[0].safety
        multiplexer = self.lockerinstance[0].mux
        program = self.lockerinstance[0].program
        if isinstance(self['scout']['page'], str):
            if self['scout']['page'].isnumeric():
                self['scout']['page'] = int(self['scout']['page'])
            else:
                self['scout']['page'] = 0
        with lock:
            if not self['ProgramActive']:
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
                scout['LaserCTRL'] |= self['scout']["bLaserCTRL"]
                self['scout']["bLaserCTRLHighlight"] = scout['LaserCTRVal']
                if self['scout']["bLaserCTRL"]:
                    scout['LaserCTRVal'] = not scout['LaserCTRVal']
                    self['scout']["bLaserCTRL"] = False
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
                        program['handmodelaserrequire'] = False
                    else:
                        safety['OpenTheDoor'] = True
                    if safety['OpenTheDoorAck']:
                        self['safety']['OpenTheDoor'] = False
                        safety['OpenTheDoor'] = False
                laser['SetChannel'] |= self['laser']['GetChannel'] 
                program['handmodelaserrequire'] |= self['laser']['GetChannel'] 
                program['handmodelaserrequire'] &= not self['laser']['ReleaseChannel'] 
                multiplexer['acquire'] |= self['laser']['GetChannel']
                laser['ReleaseChannel'] |= self['laser']['ReleaseChannel'] 
                multiplexer['release'] |= self['laser']['ReleaseChannel']
                laser['LaserTurnOn'] |= self['laser']['LaserTurnOn']
                laser['LaserTurnOff'] |= self['laser']['LaserTurnOff']
                laser['LaserReset'] |= self['laser']['ResetErrors']
            else:
                program['handmodelaserrequire'] = False
            self['scout']['ready'] = scout['status']['ReadyOn']
            self['scout']['atstart'] = scout['status']['AutoStart']
            self['scout']['alarm'] = scout['status']['Alarm']
            self['scout']['NA'] = scout['status']['rsv']
            self['scout']['progress'] = scout['status']['WeldingProgress']
            self['scout']['laseron'] = scout['status']['LaserIsOn']
            self['scout']['wobble'] = scout['status']['Wobble']
            self['scout']['connection'] = scout['StatusCheckCode']
            self['laser']['LaserIsOn'] = laser['LaserOn']
            self['laser']['LaserBusy'] = multiplexer['busy']
            self['laser']['LaserReady'] = laser['LaserReady']
            self['laser']['LaserError'] = laser['LaserError']
            self['laser']['LaserWarning'] = laser['LaserWarning']
            self['laser']['ChillerError'] = laser['ChillerError']
            self['laser']['ChillerWarning'] = laser['ChillerWarning']
            self['laser']['locklaserloop'] = laser['locklaserloop']
        self['laser']['LaserTurnOn'] = False
        self['laser']['LaserTurnOff'] = False
        self['laser']['GetChannel'] = False
        self['laser']['ReleaseChannel'] = False
        self['laser']['ResetErrors'] = False
        self['scout']['align'] = False
        self['scout']['weld'] = False
        self['scout']['alarmreset'] = False
        self['scout']['getaligninfo'] = False
        self['scout']['bAtstart'] = False
        self['scout']['bAtstop'] = False
        

    def safetyupdate(self):
        lock = self.lockerinstance[0].lock
        safety = self.lockerinstance[0].safety
        with lock:
            if safety['EstopArmed'] and safety['ZoneArmed']:
                self['statusindicators']['Safety'] = 1
            elif not safety['EstopArmed']:
                self['statusindicators']['Safety'] = -1
            elif safety['Estopresetrecquired'] or safety['Zoneresetrecquired']:
                self['statusindicators']['Safety'] = -2
            else:
                self['statusindicators']['Safety'] = 0
            self['safety']['RobotEDM'] = safety['RobotEDM']
            self['safety']['EstopArmed'] = safety['EstopArmed']
            self['safety']['DoorLocked'] = safety['DoorLocked']
            self['safety']['TroleyInside'] = safety['TroleyInside']
            self['safety']['THCPushed'] = safety['THCPushed']
            self['safety']['RobotTeachMode'] = safety['RobotTeachMode']
            self['safety']['DeadMan'] = safety['DeadMan']
            self['safety']['ZoneArmed'] = safety['ZoneArmed']
            self['safety']['Estopresetrecquired'] = safety['Estopresetrecquired']
            self['safety']['Zoneresetrecquired'] = safety['Zoneresetrecquired']
            safety['TroleyReady'] = self['safety']['TroleyReady']
            safety['TroleyReady'] |= safety['TroleyReadyForcedbyProgram']
            self['safety']['ProgramTroleyRelease'] = safety['TroleyReadyForcedbyProgram']
            if self['safety']['ProgramTroleyReleaseAcknowledged']:
                safety['TroleyReadyForcedbyProgram'] = False
                self['safety']['ProgramTroleyReleaseAcknowledged'] = False

    def pneumaticsupdate(self):
        lock = self.lockerinstance[0].lock
        pneumatics = self.lockerinstance[0].pistons
        with lock:
            if not self['ProgramActive']:
                pneumatics['TroleyPusherFront'] = self['pistoncontrol']['pusher']['Right']['coil']
                pneumatics['TroleyPusherBack'] = self['pistoncontrol']['pusher']['Left']['coil']
                pneumatics['SealUp'] = self['pistoncontrol']['seal']['Right']['coil']
                pneumatics['SealDown'] = self['pistoncontrol']['seal']['Left']['coil']
                pneumatics['ShieldingGas'] = self['pistoncontrol']['shieldinggas']['Right']['coil']
                pneumatics['HeadCooling'] = self['pistoncontrol']['headcooling']['Right']['coil']
                pneumatics['CrossJet'] = self['pistoncontrol']['crossjet']['Right']['coil']
            self['pistoncontrol']['seal']['Left']['sensor'] = pneumatics['sensorSealDown']
            self['pistoncontrol']['pusher']['Left']['sensor'] = pneumatics['sensorTroleyPusherBack']
            self['pistoncontrol']['pusher']['Right']['sensor'] = pneumatics['sensorTroleyPusherFront']
            self['pistoncontrol']['shieldinggas']['Center']['sensor'] = pneumatics['ShieldingGas']
            self['pistoncontrol']['crossjet']['Center']['sensor'] = pneumatics['sensorVacuumOk']
            self['pistoncontrol']['headcooling']['Center']['sensor'] = pneumatics['sensorAirOk']
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

    def programupdate(self):
        lock = self.lockerinstance[0].lock
        program = self.lockerinstance[0].program
        with lock:
            if self['ProgramActive']:
                self['currentposition'] = 'wiersz {}, krok {}'.format(program['cycle'], program['stepnumber'])
                self['processtime'] = (str(round(program['time'],2)))
                self['progress'] = str(program['cycle'])
                self['step'] = str(program['stepnumber'])
            self['scout']['recipes'] = list(program['recipes'])
            program['startpos'] = self.programposstart
            program['endpos'] = self.programposend
            program['ProgramName'] = self.currentProgram
            program['ProgramsFilePath'] = self.jsonpath
            program['stepmode'] = not self['auto']
            program['automode'] = self['auto']
            program['running'] = self['ProgramActive']

    def misc(self):
        self['safety']['OpenTheDoor'] |= self.internalEvents['stop']
        self.internalEvents['stop'] = False


    def update(self):
        lockerinstance = self.lockerinstance
        with lockerinstance[0].lock:
            self.alive = lockerinstance[0].console['Alive']
            errors = '\n'.join(self['widgetsettings']['ErrorCodes'][i if i in self['widgetsettings']['ErrorCodes'].keys() else '']  for i in lockerinstance[0].shared['Errcodes'])
            info = '\n'.join(self['widgetsettings']['StatusCodes'][i if i in self['widgetsettings']['StatusCodes'].keys() else ''] for i in lockerinstance[0].shared['Statuscodes'])
            if lockerinstance[0].shared['Errors']: 
                print(lockerinstance[0].shared['Errors'])
                lockerinstance[0].shared['Errors'] = ''
            self['ImportantMessages'] = errors if errors else info
            events = lockerinstance[0].events
            if self.internalEvents['buttonclicked']:
                self.internalEvents['buttonclicked'] = False
                lockerinstance[0].GPIO['somethingChanged'] = True
            self.internalEvents['error'] = events['Error']
            if self.internalEvents['ack']:
                events['ack'] = True
                self.internalEvents['ack'] = False
            if lockerinstance[0].events['Error']:
                self['ProgramActive'] = False
        self.robotupdate()
        self.scoutupdate()
        self.troleyupdate()
        self.safetyupdate()
        self.pneumaticsupdate()
        self.programupdate()
        self.misc()
        

