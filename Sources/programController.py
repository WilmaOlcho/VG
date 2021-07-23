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
            stepcomplete = lockerinstance[0].program['stepcomplete']
        if running and cycle and not cycleended and not error:
            if not stepcomplete:
                try:
                    mstring = 'step'+str(step)
                    if hasattr(self,mstring):
                        func = eval('self.'+mstring)
                        func(lockerinstance)
                except Exception as e:
                    print('step:', step, 'failed:\n',str(e))
            with lockerinstance[0].lock:
                if stepcomplete:
                    lockerinstance[0].program['stepcomplete'] = False
                    if automode:
                        step += 1
                    else:
                        lockerinstance[0].shared['Statuscodes'] = ['SD']
                if step > lockerinstance[0].program['stepnumber']:
                    lockerinstance[0].program['stepnumber'] = step


    def step(func):
        def internal(self, lockerinstance, *args, **kwargs):
            with lockerinstance[0].lock:
                steplock = lockerinstance[0].program['steplock']
            if steplock: return None
            with lockerinstance[0].lock:
                scode = "S" + str(re.search( r'\d+', func.__name__).group())
                lockerinstance[0].shared['Statuscodes'] = [scode]
            result = func(lockerinstance, *args, **kwargs)
            if result:
                print(scode,'returned', result)
                def stepexceed(l=lockerinstance):
                    with l[0].lock:
                        l[0].program['stepcomplete'] = True
                        l[0].program['steplock'] = False
                WDT(lockerinstance, errToRaise='stepfreeze', additionalFuncOnExceed = stepexceed, noerror = True, limitval = int(result), scale = 'ms')
                with lockerinstance[0].lock:
                    lockerinstance[0].program['steplock'] = True
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
            return True
        return False


    @step
    def step1(self, lockerinstance): #Scout change recipe
        #if control.Robot2State(lockerinstance, "laserlocked"):
        #    with lockerinstance[0].lock:
        #        lockerinstance[0].shared['Statuscodes'] = ['S8.2']
        #    return
        if not control.SCOUTState(lockerinstance, 'recipechanging'):
            if (control.SCOUTState(lockerinstance, 'recipe')[:-4]!= control.SCOUTState(lockerinstance, 'currentrecipe')):
                print(control.SCOUTState(lockerinstance, 'recipe')[:-4], control.SCOUTState(lockerinstance, 'currentrecipe'))
                control.SCOUTSetState(lockerinstance, 'SetRecipe')
            with lockerinstance[0].lock:
                scoutrecipe = lockerinstance[0].scout['currentrecipe']
                programrecipe = lockerinstance[0].program['programline'][control.RECIPE]
            if scoutrecipe == programrecipe[:-4]:
                return True
        return False


    @step
    def step2(self, lockerinstance): #Seal down if there is needed to change servo position
        with lockerinstance[0].lock:
            programservopos = lockerinstance[0].program['programline'][control.SERVOPOS]
        readpos = int(control.ServoState(lockerinstance,'readposition'))
        if (
            (readpos != programservopos) 
            and not control.CheckPiston(lockerinstance, "Seal", "Down")
        ):
            control.ResetPiston(lockerinstance, "Seal", "Up")
            control.SetPiston(lockerinstance, "Seal", "Down", hold=True)
        elif (
            control.CheckPiston(lockerinstance, "Seal", "Down")
            or readpos == programservopos
        ):
            return True
        return False


    @step
    def step3(self, lockerinstance): #servo positioning
        with lockerinstance[0].lock:
            programservopos = int(lockerinstance[0].program['programline'][control.SERVOPOS])
        stepinprogress = control.ServoState(lockerinstance, 'stepinprogress')
        readpos = int(control.ServoState(lockerinstance,'readposition'))
        print(programservopos, readpos)
        if not stepinprogress:
            if readpos == programservopos:
                return True
            else:
                if not control.RobotState(lockerinstance,'homepos'):
                    control.RobotSetState(lockerinstance, 'homing')  
                else:
                    control.ServoSetValue(lockerinstance, 'positionNumber', programservopos)
                    control.ServoSetState(lockerinstance, 'run')
                    control.ServoSetState(lockerinstance, 'run')
                    control.ServoSetState(lockerinstance, 'step')
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
                    time.sleep(10)
            else:
                if not control.RobotState(lockerinstance,'activecommand'):
                    return True
        return False


    @step
    def step6(self, lockerinstance): #pneumatics arming
        if control.CheckPiston(lockerinstance, "Seal", "Down"):
            control.ResetPiston(lockerinstance, "Seal", "Down")
            control.SetPiston(lockerinstance, "Seal", "Up", hold=True)
            control.setvalue(lockerinstance,"program","holdtofillwithgas",True)
            with lockerinstance[0].lock:
                lockerinstance[0].program['holdtofillwithgas'] = True
        else:
            control.SetPiston(lockerinstance, "ShieldingGas", hold=True)
            with lockerinstance[0].lock:
                holdtofillwithgas = lockerinstance[0].program['holdtofillwithgas']
            return 5000 if holdtofillwithgas else 1
        return False


    @step
    def step7(self, lockerinstance): #filling chamber with gas
        with lockerinstance[0].lock:
            holdtofillwithgas = lockerinstance[0].program['holdtofillwithgas']
            lockerinstance[0].program['holdtofillwithgas'] = False
            lockerinstance[0].shared['Statuscodes'] = ['S7.2' if holdtofillwithgas else 'S7']
        return 30000 if holdtofillwithgas else 1


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
    def step10(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['ManualAlignPage'] = lockerinstance[0].program['programline'][control.PAGE]
        if (not control.EventState(lockerinstance, 'KDrawWaitingForMessage')
            and not control.SCOUTState(lockerinstance, "ManualAlignCheck")):
            control.SCOUTSetState(lockerinstance, 'ManualAlign')
        elif control.SCOUTState(lockerinstance, "ManualAlignStatus") == 1:
            control.SetPiston(lockerinstance, "HeadCooling", hold=True)
            control.SetPiston(lockerinstance, "CrossJet", hold=True)
            return True
        elif control.SCOUTState(lockerinstance, "ManualAlignStatus"):
            print(control.SCOUTState(lockerinstance, "ManualAlignStatus"))
            return True
        return False


    @step
    def step11(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].scout['ManualWeldPage'] = lockerinstance[0].program['programline'][control.PAGE]
        if (not control.EventState(lockerinstance, 'KDrawWaitingForMessage')
            and not control.SCOUTState(lockerinstance, 'ManualWeldCheck')):
            control.SCOUTSetState(lockerinstance, 'ManualWeld')
        elif control.SCOUTState(lockerinstance, 'ManualWeldStatus') == 1:
            control.ResetPiston(lockerinstance, "HeadCooling")
            control.ResetPiston(lockerinstance, "CrossJet")
            control.ResetPiston(lockerinstance, "ShieldingGas") 
            return True
        elif control.SCOUTState(lockerinstance, 'ManualWeldStatus') != 1:
            print(control.SCOUTState(lockerinstance, 'ManualWeldStatus'))
            return True
        return False


    @step
    def step12(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['S12']
            kdrawautostart = lockerinstance[0].scout['status']['AutoStart']
            hold = lockerinstance[0].program['programline'][control.LASERHOLD]
        if hold != 'Tak':
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
