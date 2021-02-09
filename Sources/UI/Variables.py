
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
            'DumpProgramToFile':False
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

        self.auto = False
        self.processtime = 0
        self.currentposition = 0
        self.progress = 0
        self.ProgramActive = False

        self.ProcessVariables = {
            'auto':self.auto,
            'processtime':self.processtime,
            'currentposition':self.currentposition,
            'progress':self.progress
        }

        self['ImportantMessages'] = 'ass\n\n\nd\n\n\n\n\nas'