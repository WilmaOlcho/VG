import Sources.procedures as control
from Sources import EventManager, WDT
from os import listdir
from os.path import isfile, join, isdir
import re, time


import logging
_logger = logging.getLogger(__name__)

class programController(object):
    stepfreeze = False
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
        self._cycle(lockerinstance)
        self.retrievestate(lockerinstance)

    def retrievestate(self, lockerinstance):
        with lockerinstance[0].lock:
            running = lockerinstance[0].program['running']
            lockerinstance[0].program['/running'] = not running
        if running:
            self.running(lockerinstance)
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].program['stepnumber'] = 0
                if not lockerinstance[0].troley['docked']:
                    lockerinstance[0].program['cycle'] = 0
                    lockerinstance[0].program['initialised'] = False
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
            EventManager.AdaptEvent(lockerinstance, input = 'events.startprogram', edge='rising', callback = control.startprocedure, callbackargs = (lockerinstance,))
            EventManager.AdaptEvent(lockerinstance, input = 'events.stopprogram', edge='rising', callback = control.stopprocedure, callbackargs = (lockerinstance,))
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].program['running'] = False
        if not ready or not initialised:
            control.Initialise(lockerinstance)
        else:
            control.Program(lockerinstance)


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
                if hasattr(self,'step'+str(step)):
                    exec('self.step'+str(step)+"(lockerinstance)")
            except Exception as e:
                print('step:', step, 'failed:\n',str(e))
            with lockerinstance[0].lock:
                if lockerinstance[0].program['stepcomplete'] and automode:
                    lockerinstance[0].program['stepcomplete'] = False
                    step += 1
                elif lockerinstance[0].program['stepcomplete']:
                    lockerinstance[0].shared['Statuscodes'] = ['SD']
                if step > lockerinstance[0].program['stepnumber']:
                    lockerinstance[0].program['stepnumber'] = step


    def step(func, *args, **kwargs):
        def internal(self, lockerinstance, *args, **kwargs):
            if self.stepfreeze:
                return None
            with lockerinstance[0].lock:
                scode = "S" + str(re.search( r'\d+', func.__name__).group())
                lockerinstance[0].shared['Statuscodes'] = [scode]
            result = func(self, lockerinstance, *args, **kwargs)
            print('stepresult', result)
            if result != 0 and result != False:
                def stepexceed(self = self,lockerinstance=lockerinstance):
                    with lockerinstance[0].lock:
                        lockerinstance[0].program['stepcomplete'] = True
                        self.stepfreeze = False
                WDT(lockerinstance,additionalFuncOnCatch = stepexceed, additionalFuncOnExceed = stepexceed, noerror = True, limitval = int(result), scale = 's')
                self.stepfreeze = True
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
        return False


    @step
    def step1(self, lockerinstance): #Scout change recipe
        if ((control.SCOUTState(lockerinstance, 'recipe')
            != control.SCOUTState(lockerinstance, 'currentrecipe'))
            and not control.SCOUTState(lockerinstance, 'Recipechangedsuccesfully')):
            if (not control.EventState(lockerinstance, 'KDrawWaitingForMessage')
                and not re.findall(control.SCOUTState(lockerinstance, 'recipe'),control.SCOUTState(lockerinstance, 'actualmessage').decode())):
                control.SCOUTSetState(lockerinstance, 'SetRecipe')
        elif control.SCOUTState(lockerinstance, 'Recipechangedsuccesfully'):
            control.SCOUTResetState(lockerinstance, 'Recipechangedsuccesfully')
        else:
            with lockerinstance[0].lock:
                scoutrecipe = lockerinstance[0].scout['currentrecipe']
                programrecipe = lockerinstance[0].program['programline'][control.RECIPE]
            if scoutrecipe == programrecipe:
                return True
        return False


    @step
    def step2(self, lockerinstance): #Seal down if there is needed to change servo position
        with lockerinstance[0].lock:
            programservopos = lockerinstance[0].program['programline'][control.SERVOPOS]
        if ((control.ServoState(lockerinstance,'positionNumber') != programservopos) 
            and not control.CheckPiston(lockerinstance, "Seal", "Down")):
            control.ResetPiston(lockerinstance, "Seal", "Up")
            control.SetPiston(lockerinstance, "Seal", "Down", hold=True)
        elif control.CheckPiston(lockerinstance, "Seal", "Down"):
            return True
        return False


    @step
    def step3(self, lockerinstance): #servo positioning
        with lockerinstance[0].lock:
            programservopos = int(lockerinstance[0].program['programline'][control.SERVOPOS])
        if int(control.ServoState(lockerinstance,'readposition')) == programservopos:
            if (control.ServoState(lockerinstance, 'switchon') 
                or control.ServoState(lockerinstance, "operationenabled")
                or not control.ServoState(lockerinstance, "disabled")):
                control.ServoSetState(lockerinstance, 'stop')
            elif (not control.ServoState(lockerinstance, "operationenabled")
                and not control.ServoState(lockerinstance, 'switchon')
                and (control.ServoState(lockerinstance, "disabled")
                    or control.ServoState(lockerinstance, "readytoswitchon"))):
                return True
        else:
            if control.RobotState(lockerinstance,'homepos'):
                if ((control.ServoState(lockerinstance, 'readytoswitchon') 
                    or control.ServoState(lockerinstance, 'disabled') 
                    or control.ServoState(lockerinstance, 'switchon'))
                    and not control.ServoState(lockerinstance, 'fault')):
                    control.ServoSetState(lockerinstance, 'run')
                if control.ServoState(lockerinstance, "operationenabled"):
                    control.ServoSetValue(lockerinstance, 'positionNumber', programservopos)
                    if not control.ServoState(lockerinstance, 'stepinprogress'): 
                        control.ServoSetState(lockerinstance, 'step')
            else:
                control.RobotSetState(lockerinstance, 'homing')
        return False


    @step
    def step4(self, lockerinstance): #robot position setting
        with lockerinstance[0].lock:
            programtable = int(lockerinstance[0].program['programline'][control.ROBOTTABLE])
            programpos = int(lockerinstance[0].program['programline'][control.ROBOTPOS])
        if ((int(control.RobotState(lockerinstance,'setpos')) !=  programpos)
            or (int(control.RobotState(lockerinstance,'settable')) != programtable)):
            control.RobotSetValue(lockerinstance, 'settable', programtable)
            control.RobotSetValue(lockerinstance, 'setpos', programpos)
        else:
            return True
        return False


    @step
    def step5(self, lockerinstance): #robot moving
        if control.RobotState(lockerinstance, 'cycle'):
            if not control.RobotState(lockerinstance,'currentpos') == control.RobotState(lockerinstance,'setpos'):
                if not control.RobotState(lockerinstance,'activecommand'):
                    control.RobotGopos(lockerinstance,control.RobotState(lockerinstance,'setpos'))
            else:
                if not control.RobotState(lockerinstance,'activecommand'):
                    return True
        return False


    @step
    def step6(self, lockerinstance): #pneumatics arming
        holdtofillwithgas = False
        if control.CheckPiston(lockerinstance, "Seal", "Down"):
            holdtofillwithgas = True
            control.ResetPiston(lockerinstance, "Seal", "Down")
            control.SetPiston(lockerinstance, "Seal", "Up", hold=True)
            control.setvalue(lockerinstance,"program","holdtofillwithgas",True)
        else:
            control.SetPiston(lockerinstance, "ShieldingGas", hold=True)
            return 5 if holdtofillwithgas else 1
        return False


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
            control.LaserSetState(lockerinstance, "acquire")
            control.LaserSetState(lockerinstance, "SetChannel")
        if control.LaserState(lockerinstance, 'LaserError'):
            control.LaserSetState(lockerinstance, "LaserReset")
        if (control.LaserState(lockerinstance, 'onpath')
            and control.LaserState(lockerinstance, 'LaserReady')):
            return True
        return False


    @step
    def step9(self, lockerinstance):
        with lockerinstance[0].lock:
            kdrawautostart = lockerinstance[0].scout['status']['AutoStart']
        if (not control.EventState(lockerinstance, 'KDrawWaitingForMessage')
            and not kdrawautostart):
            control.SCOUTSetState(lockerinstance, 'AutostartOn')
        elif kdrawautostart:
            return True
        return False


    @step
    def sstep10(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['ManualAlignPage'] = lockerinstance[0].program['programline'][control.PAGE]
        if (not control.EventState(lockerinstance, 'KDrawWaitingForMessage')
            and not control.SCOUTState(lockerinstance, "ManualAlignCheck")):
            control.SCOUTSetState(lockerinstance, 'ManualAlign')
        elif control.SCOUTState(lockerinstance, "ManualAlignStatus") == 1:
            control.SCOUTResetState(lockerinstance, 'ManualAlignCheck')
            control.SetPiston(lockerinstance, "HeadCooling", hold=True)
            control.SetPiston(lockerinstance, "CrossJet", hold=True)
            return True
        return False
    @step
    def step10(self, lockerinstance): return True
    @step
    def step11(self, lockerinstance): return True


    @step
    def sstep11(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['ManualWeldPage'] = lockerinstance[0].program['programline'][control.PAGE]
        if (not control.EventState(lockerinstance, 'KDrawWaitingForMessage')
            and not control.SCOUTState(lockerinstance, 'ManualWeldCheck')):
            control.SCOUTSetState(lockerinstance, 'ManualWeld')
        elif control.SCOUTState(lockerinstance, 'ManualWeldStatus') == 1:
            control.SCOUTResetState(lockerinstance, "ManualWeldCheck")
            control.ResetPiston(lockerinstance, "HeadCooling")
            control.ResetPiston(lockerinstance, "CrossJet")
            control.ResetPiston(lockerinstance, "ShieldingGas")            
            return True
        elif (control.SCOUTState(lockerinstance, 'ManualWeldStatus') != 1
            and control.SCOUTState(lockerinstance, 'ManualWeldCheck')):
            return True
        return False


    @step
    def step12(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S12']
            kdrawautostart = lockerinstance[0].scout['status']['AutoStart']
            hold = lockerinstance[0].program['programline'][control.LASERHOLD]
        if not hold=='Tak':
            control.SCOUTSetState(lockerinstance, 'AutostartOff')
            if not kdrawautostart:
                control.LaserSetState(lockerinstance, "release")
                control.LaserSetState(lockerinstance, "ReleaseChannel")
                control.setvalue(lockerinstance, "program", 'laserrequire', False)           
                return True
        else:
            return True
        return False


    @step
    def step13(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S13']
            lockerinstance[0].program['cycleended'] = True
            lockerinstance[0].program['stepnumber'] = 0
        return False
