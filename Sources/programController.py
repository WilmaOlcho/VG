import Sources.procedures as control
from Sources import EventManager, WDT
from os import listdir
from os.path import isfile, join, isdir
import re


import logging
_logger = logging.getLogger(__name__)

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
            files = list(filter(lambda file: file[-4:]==".dsg",files))
            if files != recipes:
                with lockerinstance[0].lock:
                    lockerinstance[0].program['recipes'] = files

    def running(self, lockerinstance):
        safety = control.CheckSafety(lockerinstance)
        program = control.CheckProgram(lockerinstance)
        ready = control.CheckPositions(lockerinstance)
        with lockerinstance[0].lock:
            initialised = lockerinstance[0].program['initialised']
        if safety and program:
            EventManager.AdaptEvent(lockerinstance, input = 'events.startprogram', callback = control.startprocedure, callbackargs = (lockerinstance,))
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].program['running'] = False
        if not ready or not initialised:
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
        if running and cycle and not cycleended and not error:
            try:
                exec('self.step'+step+"(lockerinstance)")
            except:
                pass
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


    def step(func, *args, **kwargs):
        def internal(self, lockerinstance, *args, **kwargs):
            with lockerinstance[0].lock:
                lockerinstance[0].shared['Statuscodes'] = "S" + str(re.search( r'.*\d+', func.__name__).group())
            result = func(self, lockerinstance, *args, **kwargs)
            if result:
                stepexceed = lambda o = self, l = lockerinstance:o.stepexceed(l)
                WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = int(result), scale = 's')
            return result
        return internal


    @step
    def step0(self, lockerinstance): #Scout prepare recipe
        with lockerinstance[0].lock:
            scoutrecipe = lockerinstance[0].scout['currentrecipe']
            programrecipe = lockerinstance[0].program['programline'][control.RECIPE]
        if scoutrecipe != programrecipe:
            with lockerinstance[0].lock:
                lockerinstance[0].scout['recipe'] = programrecipe
                lockerinstance[0].scout['Recipechangedsuccesfully'] = False
            return True

    @step
    def step1(self, lockerinstance): #Scout change recipe
        if ((control.SCOUTState(lockerinstance, 'recipe')
            != control.SCOUTState(lockerinstance, 'currentrecipe'))
            and not control.SCOUTState(lockerinstance, 'Recipechangedsuccesfully')):
            if (not control.EventState(lockerinstance, 'KDrawWaitingForMessage')
                and not re.findall(control.SCOUTState(lockerinstance, 'recipe'),control.SCOUTState(lockerinstance, 'actualmessage').decode())):
                control.SCOUTSetState(lockerinstance, 'SetRecipe')
        else:
            control.SCOUTReetState(lockerinstance, 'Recipechangedsuccesfully')
            return True


    @step
    def step2(self, lockerinstance): #Seal down if there is needed to change servo position
        with lockerinstance[0].lock:
            programservopos = lockerinstance[0].program['programline'][control.SERVOPOS]
        if ((control.ServoState(lockerinstance,'positionNumber') != programservopos) 
            and not control.CheckPiston(lockerinstance, "Seal", "Down")):
            control.SetPiston(lockerinstance, "Seal", "Down")
        else:
            return True


    @step
    def step3(self, lockerinstance): #servo positioning
        with lockerinstance[0].lock:
            programservopos = lockerinstance[0].program['programline'][control.SERVOPOS]
        if (control.ServoState(lockerinstance,'positionNumber') == programservopos
            and control.ServoState(lockerinstance,'positionreached')):
            if (control.ServoState(lockerinstance, 'switchon') 
                or control.ServoState(lockerinstance, "operationenabled")):
                control.ServoSetState(lockerinstance, 'stop')
            else:
                return True
        else:
            if control.RobotState(lockerinstance,'homepos'):
                if ((control.ServoState(lockerinstance, 'readytoswitchon') 
                    or control.ServoState(lockerinstance, 'disabled') 
                    or control.ServoState(lockerinstance, 'switchon'))
                    and not control.ServoState(lockerinstance, 'fault')):
                    control.ServoSetState(lockerinstance, 'run')
                if control.ServoState(lockerinstance, "operationenabled"):
                    control.ServoSetState(lockerinstance, 'step')
            else:
                control.ServoSetState(lockerinstance, 'homing')


    @step
    def step4(self, lockerinstance): #robot position setting
        with lockerinstance[0].lock:
            programtable = lockerinstance[0].program['programline'][control.ROBOTTABLE]
            programpos = lockerinstance[0].program['programline'][control.ROBOTPOS]
        if ((control.RobotState(lockerinstance,'setpos') !=  programpos)
            or (control.RobotState(lockerinstance,'settable') != programtable)):
            control.RobotSetValue(lockerinstance, 'settable', programtable)
            control.RobotSetValue(lockerinstance, 'setpos', programpos)
        else:
            return True


    @step
    def step5(self, lockerinstance): #robot moving
        if not control.RobotState(lockerinstance,'currentpos') == control.RobotState(lockerinstance,'setpos'):
            if not control.RobotState(lockerinstance,'activecommand'):
                control.RobotGopos(lockerinstance,control.RobotState(lockerinstance,'setpos'))
        else:
            return True


    @step
    def step6(self, lockerinstance): #pneumatics arming
        holdtofillwithgas = False
        if control.CheckPiston(lockerinstance, "Seal", "Down"):
            holdtofillwithgas = True
            control.SetPiston(lockerinstance, "Seal", "Up")
            control.setvalue(lockerinstance,"program","holdtofillwithgas",True)
        else:
            control.SetPiston(lockerinstance, "ShieldingGas")
            return 5 if holdtofillwithgas else 1
    

    @step
    def step7(self, lockerinstance): #filling chamber with gas
        with lockerinstance[0].lock:
            holdtofillwithgas = lockerinstance[0].program['holdtofillwithgas']
            lockerinstance[0].shared['Statuscodes'] = ['S7.2' if holdtofillwithgas else 'S7']
        return 30 if holdtofillwithgas else 3


    @step
    def step8(self, lockerinstance):
        control.setvalue(lockerinstance, "program", 'laserrequire', True)
        if control.Robot2State(lockerinstance, "laserlocked"):
            with lockerinstance[0].lock:
                lockerinstance[0].shared['Statuscodes'] = ['S8.2']
            return
        if (not control.LaserState(lockerinstance, 'onpath') 
            or not control.LaserState(lockerinstance, 'LaserReady')):
            control.LaserSetState(lockerinstance, "SetChannel")
            control.LaserSetState(lockerinstance, "acquire")
        if control.LaserState(lockerinstance, 'LaserError'):
            control.LaserSetState(lockerinstance, "LaserReset")
        if (control.LaserState(lockerinstance, 'onpath')
            and control.LaserState(lockerinstance, 'LaserReady')):
            return True


    @step
    def step9(self, lockerinstance):
        with lockerinstance[0].lock:
            kdrawautostart = lockerinstance[0].scout['status']['AutoStart']
        if (not control.EventState(lockerinstance, 'KDrawWaitingForMessage')
            and not kdrawautostart):
            control.SCOUTSetState(lockerinstance, 'AutostartOn')
        elif kdrawautostart:
            return True

    
    @step
    def step10(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['ManualAlignPage'] = lockerinstance[0].program['programline'][control.PAGE]
        if (not control.EventState(lockerinstance, 'KDrawWaitingForMessage')
            and not control.SCOUTState(lockerinstance, "ManualAlignCheck")):
            control.SCOUTSetState(lockerinstance, 'ManualAlign')
        elif control.SCOUTState(lockerinstance, "ManualAlignCheck"):
            control.SCOUTResetState(lockerinstance, 'ManualAlignCheck')
            control.SetPiston(lockerinstance, "HeadCooling")
            control.SetPiston(lockerinstance, "CrossJet")
            return True


    @step
    def step11(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['ManualWeldPage'] = lockerinstance[0].program['programline'][control.PAGE]
        if (not control.EventState(lockerinstance, 'KDrawWaitingForMessage')
            and not control.SCOUTState(lockerinstance, 'manualweldcheck')):
            control.SCOUTSetState(lockerinstance, 'ManualWeld')
        elif control.SCOUTState(lockerinstance, 'manualweldcheck'):
            control.SCOUTResetState(lockerinstance, "ManualWeldCheck")
            control.ResetPiston(lockerinstance, "HeadCooling")
            control.ResetPiston(lockerinstance, "CrossJet")
            control.ResetPiston(lockerinstance, "ShieldingGas")            
            return True


    @step
    def step12(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S12']
            hold = lockerinstance[0].program['programline'][control.LASERHOLD]
        if not hold:
            control.LaserSetState(lockerinstance, "release")
            control.LaserSetState(lockerinstance, "ReleaseChannel")
            control.setvalue(lockerinstance, "program", 'laserrequire', False)           
        return True


    @step
    def step13(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S13']
            lockerinstance[0].program['cycleended'] = True
            lockerinstance[0].program['stepnumber'] = 0
        