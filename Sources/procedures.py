
from Sources import ErrorEventWrite
from functools import reduce
import json
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


def startauto(lockerinstance):
    with lockerinstance[0].lock:
        running = lockerinstance[0].program['running']
        if not running:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].program['running'] = True
            lockerinstance[0].program['stepnumber'] = 0
            lockerinstance[0].program['cycle'] = 0


def endprogram(lockerinstance):
    with lockerinstance[0].lock:
        running = lockerinstance[0].program['running']
        if running:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].program['running'] = False
            lockerinstance[0].program['stepcomplete'] = False
            lockerinstance[0].program['stepnumber'] = 0
            lockerinstance[0].program['cycle'] = 0


def nextstep(lockerinstance):
    with lockerinstance[0].lock:
        stepcomplete = lockerinstance[0].program['stepcomplete']
        if stepcomplete:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].program['stepcomplete'] = False
            lockerinstance[0].program['stepnumber'] +=1


def startprocedure(lockerinstance):
    with lockerinstance[0].lock:
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
        ErrorEventWrite(lockerinstance, "Przerwany obwód bezpieczeństwa!", noerror=True)
    if not zonearmed:
        ErrorEventWrite(lockerinstance, "Strefa bezpieczeństwa otwarta!", noerror=True)
    if not door:
        ErrorEventWrite(lockerinstance, "Drzwi serwisowe otwarte!", noerror=True)
    if not door:
        ErrorEventWrite(lockerinstance, "Drzwi serwisowe otwarte!", noerror=True)
    if not troley:
        ErrorEventWrite(lockerinstance, "Wózek poza pozycją bezpieczną!", noerror=True)
    if resetreq:
        ErrorEventWrite(lockerinstance, "Uzbrojenie maszyny wymagane!", noerror=True)
    if (zonearmed and estoparmed) or (robotmode and deadman):
        return True
    return False


def CheckProgram(lockerinstance):
    errmsg = ''
    programname = ''
    programpath = ''
    with lockerinstance[0].lock:
        if not lockerinstance[0].program['ProgramName'] or not lockerinstance[0].program['ProgramsFilePath']:
            errmsg = 'Program not loaded'
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
                    errmsg = 'Program is invalid'
                break
    if errmsg:
        ErrorEventWrite(lockerinstance, errmsg)
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
        #result &= ServoState(lockerinstance, 'positionNumber') == 0
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
        elif alternativepath:
            currentstate = lockerinstance[0].shared[alternativepath][state]
        else:
            ErrorEventWrite(lockerinstance, 'GetState procedure got wrong parameters')
            currentstate = -1
    return currentstate


def RobotState(lockerinstance, state):
    return GetState(lockerinstance, 'robot', state)


def ServoState(lockerinstance, state):
    return GetState(lockerinstance, 'servo', state)


def LaserState(lockerinstance, state):
    return GetState(lockerinstance, 'lcon', state, alternativepath= 'mux')


def SCOUTState(lockerinstance, state):
    return GetState(lockerinstance, 'SCOUT', state)


def SetPiston(lockerinstance, pistonname, action):
    with lockerinstance[0].lock:
        lockerinstance[0].pistons[pistonname + action] = True


def RobotGopos(lockerinstance, posnumber):
    with lockerinstance[0].lock:
        if posnumber:
            lockerinstance[0].robot['setpos'] = posnumber
            lockerinstance[0].robot['go'] = True
        else:
            lockerinstance[0].robot['homing'] = True


def ServoSetState(lockerinstance, state):
    with lockerinstance[0].lock:
        lockerinstance[0].servo[state] = True


def LaserSetState(lockerinstance, state):
    with lockerinstance[0].lock:
        lockerinstance[0].lcon[state] = True


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
                ErrorEventWrite(lockerinstance, "Initialisation step 1: Nie ma gazu")
            if not air:
                ErrorEventWrite(lockerinstance, "Initialisation step 1: Nie ma powietrza")
    if step == 1:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I1']
        #checking if robot is at home
        robothome = RobotState(lockerinstance, 'homepos')
        robotmoving = RobotState(lockerinstance, 'activecommand')
        if robothome:
            with lockerinstance[0].lock:
                lockerinstance[0].program['stepnumber'] += 1
        else:
            if not robotmoving:
                RobotGopos(lockerinstance, 0)
    if step == 2:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I2']
            lockerinstance[0].program['stepnumber'] += 1
        #checking if servo is at home
        #ServoSetState(lockerinstance, 'reset')
        #ServoSetState(lockerinstance, 'run')
        #servopos = ServoState(lockerinstance, 'positionNumber')
        #ready = ServoState(lockerinstance, 'ready')
        #if servopos == 0:
        #    with lockerinstance[0].lock:
        #        lockerinstance[0].program['stepnumber'] += 1
        #elif servopos == -1:
        #    if ready:
        #        ServoSetState(lockerinstance, 'homing')
        #else:
        #    if ready:
        #        ServoSetState(lockerinstance, 'step')   
    if step == 3:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I3']
        #checking if laser is ready
        LaserOn = LaserState(lockerinstance, 'LaserOn')
        LaserReady = LaserState(lockerinstance, 'LaserReady')
        LaserBusy = LaserState(lockerinstance, 'busy')
        LaserError = LaserState(lockerinstance, 'LaserError')
        ChillerError = LaserState(lockerinstance, 'ChillerError')
        if LaserReady and not LaserBusy:
            with lockerinstance[0].lock:
                lockerinstance[0].program['stepnumber'] += 1
        elif not LaserOn:
            LaserSetState(lockerinstance, 'LaserTurnOn')
        elif LaserBusy:
            ErrorEventWrite(lockerinstance, "Initialisation step 3: Laser Is Busy")
        elif LaserError or ChillerError:
            ErrorEventWrite(lockerinstance, "Initialisation step 3: Laser or Chiller Error")
        else:
            LaserSetState(lockerinstance, 'SetChannel')
    if step == 4:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I4']
        #checking scout
        StatusCheckCode = SCOUTState(lockerinstance, 'StatusCheckCode')
        if StatusCheckCode:
            with lockerinstance[0].lock:
                lockerinstance[0].program['stepnumber'] += 1
        else:
            ErrorEventWrite(lockerinstance, 'Błąd inicjalizacji SCOUT nie odpowiada')
    if step == 5:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I5']
        #checking vacuum
        vac = CheckPiston(lockerinstance, 'Vacuum', 'Ok')
        if vac:
            with lockerinstance[0].lock:
                lockerinstance[0].program['stepnumber'] += 1
        else:
            ErrorEventWrite(lockerinstance, 'Błąd inicjalizacji filtrowentylator nie włączony')
    if step == 6:
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = [symbol,'I5']
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
    if cycle == 0: #table is from 1
        with lockerinstance[0].lock:
            lockerinstance[0].shared['Statuscodes'] = ['C0']
            progproxy['starttime'] = time.time()
            startindex = progproxy['startpos']
        programline = loadprogramline(lockerinstance, program, startindex)
        cycle = startindex
        with lockerinstance[0].lock:
            progproxy['programline'] = programline
    if cycleended:
        cycle += 1
        with lockerinstance[0].lock:
            end = lockerinstance[0].program['endpos']
        if cycle > end:
            with lockerinstance[0].lock:
                lockerinstance[0].shared['Statuscodes'] = ['CD']
            endprogram(lockerinstance)
        else:
            programline = loadprogramline(lockerinstance, program, cycle)
            with lockerinstance[0].lock:
                progproxy['programline'] = programline

        

        
