
class Variables(dict):
    def __init__(self):
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


        self['ImportantMessages'] = ''
        self['troley'] = {
            'pushingpiston':False,
            'sensorpushingpistonback':False,
            'sensorpushingpistonfront':False,
            'servoON':False,
            'servoCOIN':False,
            'servoREADY':False,
            'servoSTEP':False,
            'servoHOMING':False,
            'servoRESET':False,
            'servoTGON':False,
            'sealpiston':False,
            'sensorsealpistonup':False,
            'sensorsealpistondown':False
        }
        self['pistoncontrol'] = {
            'seal':{
                'Left':{
                    'coil':True,
                    'sensor':False},
                'Center':{
                    'coil':False,
                    'sensor':False}
            },
            'shieldinggas':{
                'Right':{
                    'coil':True},
                'Center':{}
            },
            'crossjet':{
                'Right':{
                    'coil':True},
                'Center':{}
            },
            'headcooling':{
                'Right':{
                    'coil':True},
                'Center':{}
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
                'Włącz':'servoON',
                'Wyłącz':'-servoON',
                'Krok':'servoSTEP',
                'Bazowanie':'servoHOMING',
                'Reset':'servoRESET'},
            'lamps':{
                'Serwo włączone':'servoON',
                'Serwo na pozycji':'servoCOIN',
                'Servo gotowe':'servoREADY',
                'Serwo w ruchu':'servoTGON'}}

    def update(self):
        pass