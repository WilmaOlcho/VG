
class Variables(dict):
    def __init__(self, lockerinstance, **widgetsettings):
        self.lockerinstance = lockerinstance
        self['widgetsettings'] = widgetsettings
        self.jsonpath = ''
        self.currentProgram = ''
        self.programposstart = 0
        self.programposend = 1
        self.programcolumns = ["ID","Nr","Program SCOUT","Warstwa SCOUT","Pozycja","Robot A","Robot X","Robot Y","Robot Z"]
        self.displayedprogramcolumns = [False,True,True,True,True,True,True,True,True]
        self.columnwidths = [4,4,30,15,10,15,15,15,15]
        self.internalEvents = {
            'RefreshStartEnd':False,
            'TableRefresh':False,
            'DumpProgramToFile':False,
            'ack' : False,
            'error': True,
            'start':False,
            'stop':False
        }

        self.statusindicators = {
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
        self['processtime'] = 0
        self['currentposition'] = 0
        self['progress'] = 0
        self['ProgramActive'] = False


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
            'LaserIsOn':False,
            'GetChannel':False,
            'ResetErrors':False,
            'LaserReady':False,
            'LaserAssigned':False,
            'LaserError':False,
            'LaserWarning':False,
            'ChillerError':False,
            'ChillerWarning':False,
            'LaserBusy':False
        }
        self['pistoncontrol'] = {
            'seal':{
                'Left':{
                    'coil':True,
                    'sensor':True},
                'Center':{},
                'Right':{
                    'coil':True}
            },
            'shieldinggas':{
                'Right':{
                    'coil':True
                },
                'Center':{
                    'sensor':True
                }
            },
            'crossjet':{
                'Right':{
                    'coil':True},
                'Center':{
                    'sensor':True
                }
            },
            'headcooling':{
                'Right':{
                    'coil':True},
                'Center':{
                    'sensor':True
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
        with lockerinstance[0].lock:
            self['pistoncontrol']['seal']['Left']['sensor'] = lockerinstance[0].pistons['sensorSealDown']
            self['pistoncontrol']['pusher']['Left']['sensor'] = lockerinstance[0].pistons['sensorTroleyPusherBack']
            self['pistoncontrol']['pusher']['Right']['sensor'] = lockerinstance[0].pistons['sensorTroleyPusherFront']
            self['pistoncontrol']['shieldinggas']['Center']['sensor'] = lockerinstance[0].pistons['ShieldingGas']
            self['pistoncontrol']['crossjet']['Center']['sensor'] = lockerinstance[0].pistons['sensorVacuumOk']
            self['pistoncontrol']['headcooling']['Center']['sensor'] = lockerinstance[0].pistons['sensorAirOk']
            self['laser']['LaserIsOn'] = lockerinstance[0].lcon['LaserOn']
            self['laser']['LaserBusy'] = lockerinstance[0].mux['busy']
            self['laser']['LaserReady'] = lockerinstance[0].lcon['LaserReady']
            self['laser']['LaserError'] = lockerinstance[0].lcon['LaserError']
            self['laser']['LaserWarning'] = lockerinstance[0].lcon['LaserWarning']
            self['laser']['ChillerError'] = lockerinstance[0].lcon['ChillerError']
            self['laser']['ChillerWarning'] = lockerinstance[0].lcon['ChillerWarning']
            self['troley']['servoON'] = lockerinstance[0].servo['active']
            self['troley']['servoCOIN'] = lockerinstance[0].servo['iocoin']
            self['troley']['servoREADY'] = lockerinstance[0].servo['ioready']
            self['troley']['servoTGON'] = lockerinstance[0].servo['iotgon']
            self['troley']['TroleyDocked'] = lockerinstance[0].troley['docked']        
            self.internalEvents['error'] = lockerinstance[0].events['Error']
            self['ImportantMessages'] = lockerinstance[0].shared['Errors']
            self.alive = lockerinstance[0].console['Alive']
            if self.internalEvents['ack']:
                lockerinstance[0].events['erroracknowledge'] = True
                self.internalEvents['ack'] = False
            if not self['ProgramActive']:
                lockerinstance[0].pistons['TroleyPusherFront'] |= self['pistoncontrol']['pusher']['Right']['coil']
                lockerinstance[0].pistons['TroleyPusherBack'] |= self['pistoncontrol']['pusher']['Left']['coil']
                lockerinstance[0].pistons['SealUp'] |= self['pistoncontrol']['seal']['Right']['coil']
                lockerinstance[0].pistons['SealDown'] |= self['pistoncontrol']['seal']['Right']['coil']
                lockerinstance[0].pistons['ShieldingGas'] |= self['pistoncontrol']['shieldinggas']['Right']['coil']
                lockerinstance[0].pistons['HeadCooling'] |= self['pistoncontrol']['headcooling']['Right']['coil']
                lockerinstance[0].pistons['CrossJet'] |= self['pistoncontrol']['crossjet']['Right']['coil']
                lockerinstance[0].servo['homing'] |= self['troley']['servoHOMING']
                lockerinstance[0].servo['run'] |= self['troley']['servoRUN']
                lockerinstance[0].servo['stop'] |= self['troley']['servoSTOP']
                lockerinstance[0].servo['reset'] |= self['troley']['servoRESET']
                lockerinstance[0].servo['step'] |= self['troley']['servoSTEP']
                lockerinstance[0].lcon['SetChannel'] |= self['laser']['GetChannel']
                lockerinstance[0].lcon['LaserTurnOn'] |= self['laser']['LaserOn'] & (not lockerinstance[0].lcon['LaserOn'])
                lockerinstance[0].lcon['LaserTurnOff'] |= (not self['laser']['LaserOn']) & lockerinstance[0].lcon['LaserOn']
                lockerinstance[0].lcon['LaserReset'] |= self['laser']['GetChannel']
                lockerinstance[0].robot['go'] |= self['robot']['RobotGo']
                lockerinstance[0].robot['homing'] |= self['robot']['RobotHoming']
                lockerinstance[0].robot['settable'] = self['robot']['table']
                lockerinstance[0].robot['setpos'] = self['robot']['position']
                
                self['robot']['RobotGo'] = False
                self['robot']['RobotHoming'] = False
                self['troley']['servoRUN'] = False
                self['troley']['servoSTOP'] = False
                self['troley']['servoHOMING'] = False
                self['troley']['servoSTEP'] = False
                self['troley']['servoRESET'] = False
            
            #status
            pneumatics = lockerinstance[0].pistons
            if pneumatics['ShieldingGas'] and pneumatics['sensorShieldingGasOk']:
                self.statusindicators['ShieldingGas'] = 1
            elif pneumatics['ShieldingGas'] and not pneumatics['sensorShieldingGasOk']:
                self.statusindicators['ShieldingGas'] = -1
            else:
                self.statusindicators['ShieldingGas'] = 0
            if pneumatics['CrossJet'] and pneumatics['sensorAirOk']:
                self.statusindicators['Crossjet'] = 1
            elif pneumatics['CrossJet'] and not pneumatics['sensorAirOk']:
                self.statusindicators['Crossjet'] = -1
            else:
                self.statusindicators['Crossjet'] = 0
            if pneumatics['sensorAirOk']:
                self.statusindicators['Air'] = 1
            else:
                self.statusindicators['Air'] = 0
            if pneumatics['sensorVacuumOk']:
                self.statusindicators['VacuumFilter'] = 1
            else:
                self.statusindicators['VacuumFilter'] = 0
            self.statusindicators['Light'] = 1
            troley = lockerinstance[0].shared['troley']
            if troley['docked'] and not troley['error']:
                self.statusindicators['Troley'] = 1
            elif troley['error'] or not troley['Alive']:
                self.statusindicators['Troley'] = -1
            else:
                self.statusindicators['Troley'] = 0
            robot = lockerinstance[0].robot
            if robot['Alive'] and not robot['error']:
                self.statusindicators['Robot'] = 1
                self['robot']['actualposition'] = robot['currentpos']
                self['robot']['RobotCommandActive'] = robot['activecommand']
                self['robot']['RobotIsHome'] = robot['homepos']
                self['robot']['RobotInAPosition'] = robot['currentpos'] == robot['setpos']
                self['robot']['RobotHandMode'] = robot['handmode']
                self['robot']['RobotMotorsOn'] = robot['motors']
                self['robot']['RobotCycle'] = robot['cycle']
                self['robot']['ConnectionActive'] = robot['connection']

            elif robot['error'] or not robot['Alive']:
                self.statusindicators['Robot'] = -1
            else:
                self.statusindicators['Robot'] = 0
            safety = lockerinstance[0].safety
            if safety['EstopArmed'] and safety['ZoneArmed']:
                self.statusindicators['safety'] = 1
            elif not safety['EstopArmed']:
                self.statusindicators['safety'] = -1
            elif safety['Estopresetrecquired'] or safety['Zoneresetrecquired']:
                self.statusindicators['safety'] = -2
            else:
                self.statusindicators['safety'] = 0
