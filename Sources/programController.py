import json
import Sources.procedures as control
from Sources import EventManager, WDT, ErrorEventWrite
from os import listdir
from os.path import isfile, join, isdir
#

class programController(object):
    def __init__(self, lockerinstance, programfilepath, *args, **kwargs):
        self.Alive = True
        with lockerinstance[0].lock:
            lockerinstance[0].program['Alive'] = True
        while self.Alive:
            with lockerinstance[0].lock:
                self.Alive = lockerinstance[0].program['Alive'] and not lockerinstance[0].events['closeApplication']
            if not self.Alive: break
            self.loop(lockerinstance)

    def loop(self, lockerinstance):
        with lockerinstance[0].lock:
            automode = lockerinstance[0].program['automode']
            stepmode = lockerinstance[0].program['stepmode']
        if automode: self.automode(lockerinstance)
        if stepmode: self.stepmode(lockerinstance)
        self.retrievestate(lockerinstance)

    def retrievestate(self, lockerinstance):
        with lockerinstance[0].lock:
            running = lockerinstance[0].program['running']
            lockerinstance[0].program['/running'] = not running
        if running: self.running(lockerinstance)
        self.CheckProgramsDirectory(lockerinstance)
        if lockerinstance[0].events['Error']:
            lockerinstance[0].program['running'] = False

    def CheckProgramsDirectory(self, lockerinstance):
        with lockerinstance[0].lock:
            path = lockerinstance[0].scout['recipesdir']
            recipes = lockerinstance[0].program['recipes']
        if isdir(path):
            files = [file for file in listdir(path) if isfile(join(path, file))]
            if files != recipes:
                with lockerinstance[0].lock:
                    lockerinstance[0].program['recipes'] = files

    def running(self, lockerinstance):
        safety = control.CheckSafety(lockerinstance)
        program = control.CheckProgram(lockerinstance)
        ready = control.CheckPositions(lockerinstance)
        if safety and program:
            EventManager.AdaptEvent(lockerinstance, input = 'events.startprogram', callback = control.startprocedure, callbackargs = (lockerinstance,))
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].program['running'] = False
        if not ready:
            control.Initialise(lockerinstance)
        else:
            control.Program(lockerinstance)

    def automode(self, lockerinstance):
        self._cycle(lockerinstance)

    def stepmode(self, lockerinstance):
        self._cycle(lockerinstance)

    def _cycle(self, lockerinstance):
        with lockerinstance[0].lock:
            running = lockerinstance[0].program['running']
            cycle = lockerinstance[0].program['cycle']
            cycleended = lockerinstance[0].program['cycleended']
            step = lockerinstance[0].program['stepnumber']
            automode = lockerinstance[0].program['automode']
            lastrecipe = lockerinstance[0].scout['lastrecipe']
            scoutrecipe = lockerinstance[0].scout['recipe']
            if lockerinstance[0].program['programline']:
                programrecipe = lockerinstance[0].program['programline'][control.RECIPE]
            else:
                programrecipe = ''
        if running and cycle and not cycleended:
            with lockerinstance[0].lock: #locking whole method for event-compatibility
                if lockerinstance[0].program['stepcomplete'] and automode:
                    print(lockerinstance[0].program['stepcomplete'])
                    lockerinstance[0].program['stepcomplete'] = False
                    step += 1
                elif lockerinstance[0].program['stepcomplete']:
                    lockerinstance[0].shared['Statuscodes'] = ['SD']
                #setting recipe for scout
                if step == 0:
                    lockerinstance[0].shared['Statuscodes'] = ['S0']
                    if scoutrecipe != programrecipe:
                        lockerinstance[0].scout['recipe'] = programrecipe
                        lockerinstance[0].scout['Recipechangedsuccesfully'] = False
                    else:
                        lockerinstance[0].program['stepcomplete'] = True
                if step == 1:
                    lockerinstance[0].shared['Statuscodes'] = ['S1']
                    if scoutrecipe != lastrecipe and not lockerinstance[0].scout['Recipechangedsuccesfully']:
                        if not lockerinstance[0].events['KDrawWaitingForMessage']:
                            lockerinstance[0].scout['SetRecipe'] |= True
                    else:
                        lockerinstance[0].scout['Recipechangedsuccesfully'] = False
                        lockerinstance[0].program['stepcomplete'] = True                        
                #Setting seal down
                if step == 2:
                    lockerinstance[0].shared['Statuscodes'] = ['S2']
                    if lockerinstance[0].servo['positionNumber'] != lockerinstance[0].program['programline'][control.SERVOPOS] and not lockerinstance[0].pistons['sensorSealDown']:
                        lockerinstance[0].pistons['SealDown'] = True
                    else:
                        lockerinstance[0].program['stepcomplete'] = True                        
                #setting servo position
                if step == 3:
                    lockerinstance[0].program['stepcomplete'] = True                        
                    lockerinstance[0].shared['Statuscodes'] = ['S3']
#                    if lockerinstance[0].servo['positionNumber'] == -1:
#                        ErrorEventWrite(lockerinstance, 'servo is not ready')
#                    if lockerinstance[0].servo['positionNumber'] == lockerinstance[0].program['programline'][control.SERVOPOS]:
#                       lockerinstance[0].program['stepcomplete'] = True
#                   else:
#                        if not lockerinstance[0].servo['moving']:
#                            lockerinstance[0].servo['stepnumber'] = True
                #setting robot position
                if step == 4:
                    lockerinstance[0].program['stepcomplete'] = True                        
                    lockerinstance[0].shared['Statuscodes'] = ['S4']
#                    if lockerinstance[0].robot['setpos'] != lockerinstance[0].program['programline'][control.ROBOTPOS] or lockerinstance[0].robot['settable'] != lockerinstance[0].program['programline'][control.ROBOTTABLE]:
#                        lockerinstance[0].robot['settable'] = lockerinstance[0].program['programline'][control.ROBOTTABLE]
#                        lockerinstance[0].robot['setpos'] = lockerinstance[0].program['programline'][control.ROBOTPOS]
#                    else:
#                       lockerinstance[0].program['stepcomplete'] = True
                if step == 5:
                    lockerinstance[0].program['stepcomplete'] = True                        
                    lockerinstance[0].shared['Statuscodes'] = ['S5']
#                    if lockerinstance[0].robot['currentpos'] != lockerinstance[0].program['programline'][control.ROBOTPOS]:
#                        if not lockerinstance[0].robot['activecommand']:
#                            lockerinstance[0].robot['go'] = True
#                    else:
#                       lockerinstance[0].program['stepcomplete'] = True
                #Setting seal up
                if step == 6:
                    lockerinstance[0].shared['Statuscodes'] = ['S6']
                    if lockerinstance[0].pistons['sensorSealDown']:
                        lockerinstance[0].pistons['SealUp'] = True
                    else:
                        lockerinstance[0].program['stepcomplete'] = True                        
            #Wait 3s until sealing were perfect
            if step == 7:
                with lockerinstance[0].lock:
                    lockerinstance[0].shared['Statuscodes'] = ['S7']
                def exceed(lockerinstance = lockerinstance):
                    with lockerinstance[0].lock:
                        lockerinstance[0].program['stepcomplete'] = True
                WDT(lockerinstance,additionalFuncOnCatch = exceed, additionalFuncOnExceed = exceed, noerror = True, limitval = 3, scale = 's')
            with lockerinstance[0].lock:
                #scout atstart
                if step == 8:
                    lockerinstance[0].shared['Statuscodes'] = ['S8']
                    if not lockerinstance[0].events['KDrawWaitingForMessage']:
                        lockerinstance[0].scout['AutostartOn'] = True
                    if lockerinstance[0].scout['status']['AutoStart']:
                        lockerinstance[0].program['stepcomplete'] = True                          
                #align scout
                if step == 9:
                    lockerinstance[0].shared['Statuscodes'] = ['S9']
                    lockerinstance[0].scout['ManualAlignPage'] = lockerinstance[0].program['programline'][control.PAGE]
                    if not lockerinstance[0].events['KDrawWaitingForMessage']:
                        lockerinstance[0].scout['ManualAlign'] = True
                    if lockerinstance[0].scout['ManualAlignCheck']:
                        lockerinstance[0].scout['ManualAlignCheck'] = False
                        lockerinstance[0].program['stepcomplete'] = True                          
                #SCOUT weld
                if step == 10:
                    lockerinstance[0].shared['Statuscodes'] = ['S10']
                    lockerinstance[0].scout['ManualWeldPage'] = lockerinstance[0].program['programline'][control.PAGE]
                    if not lockerinstance[0].events['KDrawWaitingForMessage']:
                        lockerinstance[0].scout['ManualWeld'] = True
                    if lockerinstance[0].scout['ManualWeldCheck']:
                        lockerinstance[0].scout['ManualWeldCheck'] = False
                        lockerinstance[0].program['stepcomplete'] = True                          
                if step == 11:
                    lockerinstance[0].shared['Statuscodes'] = ['S11']
                    lockerinstance[0].program['cycleended'] = True
                    lockerinstance[0].program['stepnumber'] = 0
                    step = 0
                    print('poszło')
                if step > lockerinstance[0].program['stepnumber']:
                    lockerinstance[0].program['stepnumber'] = step
