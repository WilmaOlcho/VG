from Sources.common import EventManager
from Sources import ErrorEventWrite
from Sources.TactWatchdog import TactWatchdog
WDT = TactWatchdog.WDT
import json, re
import time
from pathlib import Path

##Constants
ID = 0
STEP = 1
RECIPE = 2
PAGE = 3
ROBOTPOS = 4
ROBOTTABLE = 5
SERVOPOS = 6
LASERHOLD = 7


import logging
_logger = logging.getLogger(__name__)

def startauto(lockerinstance):
    with lockerinstance[0].lock:
        if not lockerinstance[0].program['running']:
            lockerinstance[0].program['running'] = True
            lockerinstance[0].program['stepnumber'] = 0


def endprogram(lockerinstance):
    RobotGopos(lockerinstance,0)
    def robend(lockerinstance = lockerinstance):
        ServoSetState(lockerinstance, 'run')
        ServoSetState(lockerinstance, 'run')
        ServoSetValue(lockerinstance, 'positionNumber', 1)
        ServoSetState(lockerinstance, 'step')
        def end(lockerinstance = lockerinstance):
            pass #oddac sterowanie wozkiem
        EventManager.AdaptEvent(lockerinstance,input = 'servo.stepinprogress', edge='falling', callback = end)
    EventManager.AdaptEvent(lockerinstance,input = 'robot.homepos', callback = robend)
    with lockerinstance[0].lock:
        if lockerinstance[0].program['running']:
            lockerinstance[0].program['running'] = False
            lockerinstance[0].program['stepcomplete'] = False
            lockerinstance[0].program['stepnumber'] = 0
            lockerinstance[0].program['cycle'] = 0

def nextstep(lockerinstance):
    with lockerinstance[0].lock:
        if lockerinstance[0].program['stepcomplete']:
            lockerinstance[0].program['stepcomplete'] = False
            lockerinstance[0].program['stepnumber'] +=1


def stopprocedure(lockerinstance):
    with lockerinstance[0].lock:
        lockerinstance[0].events['stopprogram'] = False
        running = lockerinstance[0].program['running']
    if not running: endprogram(lockerinstance)


def startprocedure(lockerinstance):
    with lockerinstance[0].lock:
        lockerinstance[0].events['startprogram'] = False
        step, auto = lockerinstance[0].program['stepmode'], lockerinstance[0].program['automode']
    if auto: startauto(lockerinstance)
    if step: nextstep(lockerinstance)

def CheckSafety(lockerinstance):
    with lockerinstance[0].lock:
        zonearmed = lockerinstance[0].safety['ZoneArmed']
        estoparmed = lockerinstance[0].safety['EstopArmed']
        robotmode = lockerinstance[0].safety['RobotTeachMode']
        resetreq = lockerinstance[0].safety['Zoneresetrecquired'] or lockerinstance[0].safety['Estopresetrecquired']
        deadman = lockerinstance[0].safety['DeadMan']
        door = lockerinstance[0].safety['DoorClosed']
        troley = lockerinstance[0].safety['TroleyInside']
    if not estoparmed:
        ErrorEventWrite(lockerinstance, errcode = "10", noerror=True)
    if not zonearmed:
        ErrorEventWrite(lockerinstance, errcode = "11", noerror=True)
    if not door:
        ErrorEventWrite(lockerinstance, errcode = "12", noerror=True)
    if not troley:
        ErrorEventWrite(lockerinstance, errcode = "13", noerror=True)
    if resetreq:
        ErrorEventWrite(lockerinstance, errcode = "14", noerror=True)
    if (zonearmed and estoparmed) or (robotmode and deadman):
        return True
    return False


def CheckProgram(lockerinstance):
    errcode = ''
    programname = ''
    programpath = ''
    with lockerinstance[0].lock:
        if not lockerinstance[0].program['ProgramName'] or not lockerinstance[0].program['ProgramsFilePath']:
            errcode = '16'
        else:
            programname = lockerinstance[0].program['ProgramName']
            programpath = lockerinstance[0].program['ProgramsFilePath']
    if programname and programpath:
        with open(programpath, 'r') as jsonfile:
            programs = json.load(jsonfile)
        for program in programs['Programs']:
            if program['Name'] == programname:
                recipesarepresent = checkrecipes(lockerinstance, program)
                if not recipesarepresent:
                    errcode = '15'
                break
    if errcode:
        ErrorEventWrite(lockerinstance, errcode = errcode)
        return False
    else:
        return True


def CheckPositions(lockerinstance):
    with lockerinstance[0].lock:
        initialised = lockerinstance[0].program['initialised']
        initialising = lockerinstance[0].program['initialising']
    if not initialised:
        result = CheckPiston(lockerinstance, 'Seal', 'Down')
        result &= RobotState(lockerinstance, 'homepos')
        result &= ServoState(lockerinstance, 'homepositionisknown')
        result &= CheckPiston(lockerinstance, 'Air', 'Ok')
        result &= CheckPiston(lockerinstance, 'ShieldingGas', 'Ok')
        result &= CheckPiston(lockerinstance, 'Vacuum', 'Ok')
    elif initialising:
        result = False
    else:
        result = True
    return result


def CheckPiston(lockerinstance, pistonname, action):
    with lockerinstance[0].lock:
        pistonState = lockerinstance[0].pistons['sensor' + pistonname + action]
    return pistonState


def GetState(lockerinstance, path, state, alternativepath = ''):
    with lockerinstance[0].lock:
        if state in lockerinstance[0].shared[path].keys():
            currentstate = lockerinstance[0].shared[path][state]
            #print('lockerinstance[0].',path,state,' is ',currentstate)
        elif alternativepath:
            currentstate = lockerinstance[0].shared[alternativepath][state]
            #print('lockerinstance[0].',alternativepath,state,' is ',currentstate)
        else:
            _logger.debug('GetState procedure got wrong parameters')
            currentstate = -1
    return currentstate

def setvalue(lockerinstance, branch, register, value):
    #print('lockerinstance.shared[{}][{}] = {}'.format(branch, register, value))
    with lockerinstance[0].lock:
        lockerinstance[0].shared[branch][register] = value


def ServoState(lockerinstance, state):
    return GetState(lockerinstance, 'servo', state)

def EventState(lockerinstance, state):
    return GetState(lockerinstance, 'events', state)

def ServoSetState(lockerinstance, state):
    setvalue(lockerinstance, 'servo', state, True)

def ServoSetValue(lockerinstance, state, value):
    setvalue(lockerinstance, 'servo', state, value)

def LaserSetState(lockerinstance, state):
    lcon = False
    with lockerinstance[0].lock:
        if state in lockerinstance[0].shared['lcon'].keys():
            lcon = True
    if lcon:
        setvalue(lockerinstance, 'lcon', state, True)
    else:
        setvalue(lockerinstance, 'mux', state, True)

def LaserResetState(lockerinstance, state):
    with lockerinstance[0].lock:
        if state in lockerinstance[0].shared['lcon'].keys():
            setvalue(lockerinstance, 'lcon', state, False)
        else:
            setvalue(lockerinstance, 'mux', state, False)

def LaserState(lockerinstance, state):
    return GetState(lockerinstance, 'lcon', state, alternativepath= 'mux')

def SCOUTState(lockerinstance, state):
    return GetState(lockerinstance, 'SCOUT', state)

def SCOUTSetState(lockerinstance, state):
    setvalue(lockerinstance, 'SCOUT', state, True)

def SCOUTResetState(lockerinstance, state):
    setvalue(lockerinstance, 'SCOUT', state, False)


def SetPiston(lockerinstance, pistonname, action= '', hold = False):
    def holdpiston(lockerinstance= lockerinstance, pname = pistonname, paction = action):
        import threading as thr
        name = thr.currentThread().name
        with lockerinstance[0].lock:
            if not lockerinstance[0].program['running']:
                if name in lockerinstance[0].wdt:
                    lockerinstance[0].wdt.remove(name)
                return None
        if paction:
            setvalue(lockerinstance, 'pistons', pname + action, True)
        else:
            setvalue(lockerinstance, 'pistons', pname, True)
    if hold:
        WDT(lockerinstance, errToRaise= pistonname + action + 'hold',limitval=10, scale='y', noerror=True, additionalFuncOnLoop=holdpiston)
    else:
        holdpiston()

def ResetPiston(lockerinstance, pistonname, action = ''):
    if action:
        setvalue(lockerinstance, 'pistons', pistonname + action, False)
    else:
        setvalue(lockerinstance, 'pistons', pistonname, False)
    with lockerinstance[0].lock:
        for i, hpiston in enumerate(lockerinstance[0].wdt):
            sample = re.findall(pistonname + action + 'hold',hpiston)
            if sample:
                lockerinstance[0].wdt.remove(lockerinstance[0].wdt[i])
                break


def RobotState(lockerinstance, state):
    return GetState(lockerinstance, 'robot', state)

def RobotSetState(lockerinstance, state):
    setvalue(lockerinstance, 'robot', state, True)

def RobotSetValue(lockerinstance, state, value):
    setvalue(lockerinstance, 'robot', state, value)

def RobotResetState(lockerinstance, state):
    setvalue(lockerinstance, 'robot', state, False)

def Robot2State(lockerinstance, state):
    return GetState(lockerinstance, 'robot2', state)

def Robot2SetState(lockerinstance, state):
    setvalue(lockerinstance, 'robot2', state, True)

def Robot2SetValue(lockerinstance, state, value):
    setvalue(lockerinstance, 'robot2', state, value)

def Robot2ResetState(lockerinstance, state):
    setvalue(lockerinstance, 'robot2', state, False)

def RobotGopos(lockerinstance, posnumber):
    with lockerinstance[0].lock:
        if posnumber:
            lockerinstance[0].robot['setpos'] = posnumber
            lockerinstance[0].robot['go'] |= True
        else:
            lockerinstance[0].robot['homing'] |= True


def Initialise(lockerinstance):
    with lockerinstance[0].lock:
        step = lockerinstance[0].program['stepnumber']
        lockerinstance[0].program['initialising'] = True
        currenttime = time.time()
        if (currenttime - lockerinstance[0].shared['Steptime'])%3 < 1:
            symbol = 'I.'
        elif (currenttime - lockerinstance[0].shared['Steptime'])%3 < 2:
            symbol = 'I..'
        elif (currenttime - lockerinstance[0].shared['Steptime'])%3 < 3:
            symbol = 'I...'
        else:
            symbol = 'I'
    if step == 0:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I0']
        #checking if seal piston is down
        sealdown = CheckPiston(lockerinstance, 'Seal', 'Down')
        #checking if compressed air is present
        air = CheckPiston(lockerinstance, 'Air', 'Ok')
        #checking if argon air is present
        gas = CheckPiston(lockerinstance, 'ShieldingGas', 'Ok')
        if sealdown and air and gas:
            with lockerinstance[0].lock:
                lockerinstance[0].program['stepnumber'] += 1
        elif not sealdown:
            SetPiston(lockerinstance, 'Seal', 'Down')
        else:
            if not gas:
                ErrorEventWrite(lockerinstance, errcode = "17")
            if not air:
                ErrorEventWrite(lockerinstance, errcode ="18")
    if step == 1:
        #checking if robot is at home
        if RobotState(lockerinstance, 'cycle'):
            with lockerinstance[0].lock:
                lockerinstance[0].shared['Statuscodes'] = [symbol,'I1']
            if RobotState(lockerinstance, 'homepos'):
                with lockerinstance[0].lock:
                    lockerinstance[0].program['stepnumber'] += 1
            else:
                if not RobotState(lockerinstance, 'activecommand'):
                    RobotGopos(lockerinstance, 0)
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].shared['Statuscodes'] = [symbol,'I1.2']
    if step == 2:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I2']
        if not ServoState(lockerinstance, "hominginprogress"):
            if ServoState(lockerinstance, 'homepositionisknown'):
                if int(ServoState(lockerinstance, 'readposition')):
                    with lockerinstance[0].lock:
                        lockerinstance[0].program['stepnumber'] += 1
                else:
                    ServoSetValue(lockerinstance,'positionNumber', 1)
                    ServoSetState(lockerinstance,'step')
            else:
                ServoSetState(lockerinstance, 'homing')
    if step == 3:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I3']
        #checking if laser is ready
        if (LaserState(lockerinstance, 'LaserOn')
            and not LaserState(lockerinstance, 'LaserError')):
            with lockerinstance[0].lock:
                lockerinstance[0].program['stepnumber'] += 1
        elif not LaserState(lockerinstance, 'LaserOn'):
            LaserSetState(lockerinstance, 'LaserTurnOn')
        elif (LaserState(lockerinstance, 'LaserError')
            or LaserState(lockerinstance, 'ChillerError')):
            ErrorEventWrite(lockerinstance, errcode ="20")
    if step == 4:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I4']
        #checking scout
        if SCOUTState(lockerinstance, 'StatusCheckCode'):
            with lockerinstance[0].lock:
                lockerinstance[0].program['stepnumber'] += 1
        else:
            ErrorEventWrite(lockerinstance, errcode ="21")
    if step == 5:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I5']
        #checking vacuum
        vac = CheckPiston(lockerinstance, 'Vacuum', 'Ok')
        if vac:
            with lockerinstance[0].lock:
                lockerinstance[0].program['stepnumber'] += 1
        else:
            ErrorEventWrite(lockerinstance, errcode ="22")
    if step == 6:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I6']
            lockerinstance[0].program['cycle'] = 0
            lockerinstance[0].program['stepnumber'] = 0            
            lockerinstance[0].program['initialising'] = False
            lockerinstance[0].program['initialised'] = True


def checkrecipes(lockerinstance, program):
    for recipe in [line[RECIPE] for line in program['Table']]:
        if recipe:
            with lockerinstance[0].lock:
                path = lockerinstance[0].scout['recipesdir']
            if Path(path + "/" + recipe).is_file() and path and recipe:
                continue
            else:
                return False
    return True


def loadprogramline(lockerinstance, program, number):
    #program dict with key table, where is list of lists of 9 elements each
    while True:
        result = list(filter(lambda x: x[STEP] == number, program['Table']))
        if result:
            with lockerinstance[0].lock:
                lockerinstance[0].program['cycle'] = number
                lockerinstance[0].program['programline'] = result[0]
            print(result[0])
            return result[0]
        else: number +=1
        with lockerinstance[0].lock:
            maxintable = lockerinstance[0].program['endpos']
        if number >= maxintable: break
    

def Program(lockerinstance):
    progproxy = lockerinstance[0].program
    with lockerinstance[0].lock:
        cycle = progproxy['cycle']
        programspath = progproxy['ProgramsFilePath']
        programname = progproxy['ProgramName']
        cycleended = progproxy['cycleended']
        end = progproxy['endpos']
        if cycleended: progproxy['cycleended'] = False
        progproxy['currenttime'] = time.time()
        if progproxy['running']:
            progproxy['time'] = progproxy['currenttime'] - progproxy['starttime']
        else:
            progproxy['starttime'] = time.time()
            progproxy['time'] = 0.0
    with open(programspath, 'r') as jsonfile:
        programs = json.load(jsonfile)
    program = list(filter(lambda x: x['Name'] == programname, programs['Programs']))[0]
    if int(ServoState(lockerinstance,'readposition')) == 0:
        with lockerinstance[0].lock:
            progproxy['initialised'] = False
    if cycle == 0: #table is from 1
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['C0']
            progproxy['starttime'] = time.time()
            startindex = progproxy['startpos']
        loadprogramline(lockerinstance, program, startindex)
        cycle = startindex  
    if cycle > end:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['CD']
        endprogram(lockerinstance)
    elif cycleended:
        cycle += 1
        programline = loadprogramline(lockerinstance, program, cycle)
        with lockerinstance[0].lock:
            progproxy['cycle'] = cycle
            progproxy['stepnumber']=0
            progproxy['programline'] = programline
            progproxy['cycleended'] = False
            lockerinstance[0].scout['ManualAlignCheck'] = False
            lockerinstance[0].scout['ManualWeldCheck'] = False
            lockerinstance[0].scout['recipechanging'] = False
            lockerinstance[0].scout['photosshooting'] = False
            lockerinstance[0].scout['weldinginprogress'] = False

        

        
