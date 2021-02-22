
class Variables(dict):
    def __init__(self, lockerinstance, **widgetsettings):
        self.lockerinstance = lockerinstance
        self['widgetsettings'] = widgetsettings
        self.jsonpath = ''
        self.currentProgram = ''
        self.programposstart = 0
        self.programposend = 1
        self.programcolumns = ["ID","Nr","Program SCOUT","Warstwa SCOUT","Pozycja","Robot A","Robot X","Robot Y","Robot Z"]
        self.displayedprogramcolumns = [False,True,True,True,True,False,False,False,False]
        self.columnwidths = [4,4,30,15,10,8,8,8,8]
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
        self['servocontrol'] = {
            'buttons':{
                'Włącz':'servoRUN',
                'Wyłącz':'servoSTOP',
                'Krok':'servoSTEP',
                'Bazowanie':'servoHOMING',
                'Reset':'servoRESET'},
            'lamps':{
                'Serwo włączone':'servoON',
                'Serwo na pozycji':'servoCOIN',
                'Serwo gotowe':'servoREADY',
                'Serwo w ruchu':'servoTGON',
                'Wózek zadokowany':'TroleyDocked'}}
        self.Alive = True

    def update(self):
        lockerinstance = self.lockerinstance
        lockerinstance[0].lock.acquire()
        self['pistoncontrol']['seal']['Left']['sensor'] = lockerinstance[0].pistons['sensorSealDown']
        self['pistoncontrol']['pusher']['Left']['sensor'] = lockerinstance[0].pistons['sensorTroleyPusherBack']
        self['pistoncontrol']['pusher']['Right']['sensor'] = lockerinstance[0].pistons['sensorTroleyPusherFront']
        self['pistoncontrol']['shieldinggas']['Center']['sensor'] = lockerinstance[0].pistons['ShieldingGas']
        self['pistoncontrol']['crossjet']['Center']['sensor'] = lockerinstance[0].pistons['sensorVacuumOk']
        self['pistoncontrol']['headcooling']['Center']['sensor'] = lockerinstance[0].pistons['sensorAirOk']
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
            lockerinstance[0].pistons['TroleyPusherFront'] = self['pistoncontrol']['pusher']['Right']['coil']
            lockerinstance[0].pistons['TroleyPusherBack'] = self['pistoncontrol']['pusher']['Left']['coil']
            lockerinstance[0].pistons['SealUp'] = self['pistoncontrol']['seal']['Right']['coil']
            lockerinstance[0].pistons['SealDown'] = self['pistoncontrol']['seal']['Right']['coil']
            lockerinstance[0].pistons['ShieldingGas'] = self['pistoncontrol']['shieldinggas']['Right']['coil']
            lockerinstance[0].pistons['HeadCooling'] = self['pistoncontrol']['headcooling']['Right']['coil']
            lockerinstance[0].pistons['CrossJet'] = self['pistoncontrol']['crossjet']['Right']['coil']
            lockerinstance[0].servo['homing'] = self['troley']['servoHOMING']
            lockerinstance[0].servo['run'] = self['troley']['servoRUN']
            lockerinstance[0].servo['stop'] = self['troley']['servoSTOP']
            lockerinstance[0].servo['reset'] = self['troley']['servoRESET']
            lockerinstance[0].servo['step'] = self['troley']['servoSTEP']

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
        elif robot['error'] or not robot['Alive']:
            self.statusindicators['Robot'] = -1
        else:
            self.statusindicators['Robot'] = 0
        #TODO safety
        lockerinstance[0].lock.release()
