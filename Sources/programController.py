import json
import Sources.procedures as control
from Sources import EventManager, WDT, ErrorEventWrite
from os import listdir
from os.path import isfile, join, isdir
import re
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
            files = list(filter(lambda file: file[:4]==".dsg",files))
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
            error = lockerinstance[0].events['Error']
            if lockerinstance[0].program['programline']:
                programrecipe = lockerinstance[0].program['programline'][control.RECIPE]
            else:
                programrecipe = ''
        if running and cycle and not cycleended and not error:
            if step == 0: self.step0(lockerinstance)
            if step == 1: self.step1(lockerinstance)
            if step == 2: self.step2(lockerinstance)
            if step == 3: self.step3(lockerinstance)
            if step == 4: self.step4(lockerinstance)
            if step == 5: self.step5(lockerinstance)
            if step == 6: self.step6(lockerinstance)                 
            if step == 7: self.step7(lockerinstance)
            if step == 8: self.step8(lockerinstance)
            if step == 9: self.step9(lockerinstance)
            if step == 10: self.step10(lockerinstance)                        
            if step == 11: self.step11(lockerinstance)
            if step == 12: self.step12(lockerinstance)
            if step == 13: self.step13(lockerinstance)
            if step == 14: self.step14(lockerinstance)
            with lockerinstance[0].lock:
                if lockerinstance[0].program['stepcomplete'] and automode:
                    lockerinstance[0].program['stepcomplete'] = False
                    step += 1
                elif lockerinstance[0].program['stepcomplete']:
                    lockerinstance[0].shared['Statuscodes'] = ['SD']
                if step > lockerinstance[0].program['stepnumber']:
                    lockerinstance[0].program['stepnumber'] = step

    def stepexceed(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].program['stepcomplete'] = True

    def step0(self, lockerinstance): #Scout prepare recipe
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S0']
            scoutrecipe = lockerinstance[0].scout['currentrecipe']
            programrecipe = lockerinstance[0].program['programline'][control.RECIPE]
        if scoutrecipe != programrecipe:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['recipe'] = programrecipe
                lockerinstance[0].scout['Recipechangedsuccesfully'] = False
        stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
        WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')

    def step1(self, lockerinstance): #Scout change recipe
        with lockerinstance[0].lock: 
            lockerinstance[0].shared['Statuscodes'] = ['S1']
            scoutrecipe = lockerinstance[0].scout['recipe']
            lastrecipe = lockerinstance[0].scout['currentrecipe']
            recipechanged = lockerinstance[0].scout['Recipechangedsuccesfully']
            kdrawwaiting = lockerinstance[0].events['KDrawWaitingForMessage']
            actmessage = lockerinstance[0].scout['actualmessage']
        if scoutrecipe != lastrecipe and not recipechanged:
            if not kdrawwaiting and not re.findall(scoutrecipe,actmessage.decode()):
                with lockerinstance[0].lock:
                    lockerinstance[0].scout['SetRecipe'] |= True
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['Recipechangedsuccesfully'] = False
            stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
            WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')
    
    def step2(self, lockerinstance): #Seal down if there is needed to change servo position
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S2']
            servopos = lockerinstance[0].servo['positionNumber']
            programservopos = lockerinstance[0].program['programline'][control.SERVOPOS]
            sealdown = lockerinstance[0].pistons['sensorSealDown']
        if (servopos != programservopos) and not sealdown:
            with lockerinstance[0].lock:
                lockerinstance[0].pistons['SealDown'] = True
        else:
            stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
            WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')


    def step3(self, lockerinstance): #servo positioning
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S3']
            servopos = lockerinstance[0].servo['positionNumber']
            posreached = lockerinstance[0].servo['positionreached']
            programservopos = lockerinstance[0].program['programline'][control.SERVOPOS]
            robothome = lockerinstance[0].robot['homepos']
            switchon = lockerinstance[0].servo['switchon']
            operationenabled = lockerinstance[0].servo['operationenabled']
            disabled = lockerinstance[0].servo['disabled']
            readytoswitchon = lockerinstance[0].servo['readytoswitchon']
            fault = lockerinstance[0].servo['fault']
        if servopos == programservopos and posreached:
            if switchon or operationenabled:
                with lockerinstance[0].lock:
                    lockerinstance[0].servo['stop'] = True
            else:
                stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
                WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')
        else:
            if robothome:
                if (readytoswitchon or disabled or switchon) and not fault:
                    with lockerinstance[0].lock:
                        lockerinstance[0].servo['run'] = True
                if operationenabled:
                    with lockerinstance[0].lock:
                        lockerinstance[0].servo['step'] = True
            else:
                with lockerinstance[0].lock:
                    lockerinstance[0].robot['homing'] = True
    
    def step4(self, lockerinstance): #robot position setting
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S4']
            programtable = lockerinstance[0].program['programline'][control.ROBOTTABLE]
            programpos = lockerinstance[0].program['programline'][control.ROBOTPOS]
            robotpostable = lockerinstance[0].robot['settable']
            robotpos = lockerinstance[0].robot['setpos']
        if (robotpos !=  programpos) or (robotpostable != programtable):
            with lockerinstance[0].lock:
                lockerinstance[0].robot['settable'] = programtable
                lockerinstance[0].robot['setpos'] = programpos
        else:
            stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
            WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')
    
    def step5(self, lockerinstance): #robot moving
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S5']
            robotinpos = lockerinstance[0].robot['currentpos'] == lockerinstance[0].robot['setpos']
            robotincommand = lockerinstance[0].robot['activecommand']
        if not robotinpos:
            if not robotincommand:
                with lockerinstance[0].lock:
                    lockerinstance[0].robot['go'] = True
        else:
            stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
            WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')
    
    def step6(self, lockerinstance): #pneumatics arming
        holdtofillwithgas = False
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S6']
            sealdown = lockerinstance[0].pistons['sensorSealDown']
        if sealdown:
            holdtofillwithgas = True
            with lockerinstance[0].lock:
                lockerinstance[0].pistons['SealUp'] = True
                lockerinstance[0].program['holdtofillwithgas'] = holdtofillwithgas
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].pistons['ShieldingGas'] = True 
            stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
            WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 5 if holdtofillwithgas else 1, scale = 's')
    
    def step7(self, lockerinstance): #filling chamber with gas
        with lockerinstance[0].lock:
            holdtofillwithgas = lockerinstance[0].program['holdtofillwithgas']
            lockerinstance[0].shared['Statuscodes'] = ['S7.2' if holdtofillwithgas else 'S7']
        stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
        WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 30 if holdtofillwithgas else 3, scale = 's')
    

    def step8(self, lockerinstance):
        with lockerinstance[0].lock:
            laserisbusy = lockerinstance[0].robot2['laserlocked']
            lockerinstance[0].program['laserrequire'] = True
        if laserisbusy:
            with lockerinstance[0].lock:
                lockerinstance[0].shared['Statuscodes'] = ['S8.2']
            return
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S8']
            onpath = lockerinstance[0].mux['onpath']
            LaserReady = lockerinstance[0].lcon['LaserReady']
            LaserError = lockerinstance[0].lcon['LaserError']
        if not onpath or not LaserReady:
            lockerinstance[0].lcon['SetChannel'] = True
            lockerinstance[0].mux['acquire'] = True
        if LaserError:
            lockerinstance[0].lcon['LaserReset']
        if onpath and LaserReady:
            stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
            WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')
    
    def step9(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S9']
            kdrawwaiting = lockerinstance[0].events['KDrawWaitingForMessage']
            kdrawautostart = lockerinstance[0].scout['status']['AutoStart']
        if not kdrawwaiting and not kdrawautostart:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['AutostartOn'] = True
        elif kdrawautostart:
            stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
            WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')
    
    def step10(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S10']
            lockerinstance[0].scout['ManualAlignPage'] = lockerinstance[0].program['programline'][control.PAGE]
            kdrawwaiting = lockerinstance[0].events['KDrawWaitingForMessage']
            kdrawmanualaligncheck = lockerinstance[0].scout['ManualAlignCheck']
        if not kdrawwaiting and not kdrawmanualaligncheck:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['ManualAlign'] = True
        elif kdrawmanualaligncheck:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['ManualAlignCheck'] = False
                lockerinstance[0].pistons['HeadCooling'] = True
                lockerinstance[0].pistons['CrossJet'] = True
            stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
            WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')


    def step11(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S11']
            lockerinstance[0].scout['ManualWeldPage'] = lockerinstance[0].program['programline'][control.PAGE]
            kdrawwaiting = lockerinstance[0].events['KDrawWaitingForMessage']
            manualweldcheck = lockerinstance[0].scout['manualweldcheck']
        if not kdrawwaiting and not manualweldcheck:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['ManualWeld'] = True
        elif manualweldcheck:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['ManualWeldCheck'] = False
                lockerinstance[0].pistons['HeadCooling'] = False
                lockerinstance[0].pistons['CrossJet'] = False                         
                lockerinstance[0].pistons['ShieldingGas'] = False 
            stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
            WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')
   

    def step12(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S12']
            hold = lockerinstance[0].program['programline'][control.LASERHOLD]
        if not hold:
            with lockerinstance[0].lock:
                lockerinstance[0].mux['release'] = True
                lockerinstance[0].lcon['ReleaseChannel'] = True            
                lockerinstance[0].program['laserrequire'] = False            
        stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
        WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = 1, scale = 's')


    def step13(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S13']
            lockerinstance[0].program['cycleended'] = True
            lockerinstance[0].program['stepnumber'] = 0
        step = 0
        