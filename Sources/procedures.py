
from Sources import ErrorEventWrite
from functools import reduce
import json
import time
from Pathlib import Path

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
            lockerinstance[0].program['stepcomplete'] = False
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
            lockerinstance[0].program['stepnumber'] += 1
            lockerinstance[0].program['cycle'] = 0

def startprocedure(lockerinstance):
    with lockerinstance[0].lock:
        step, auto = lockerinstance[0].program['stepmode'], lockerinstance[0].program['automode']
    if auto: startauto(lockerinstance)
    if step: nextstep(lockerinstance)

def CheckSafety(lockerinstance):
    return False

def CheckProgram(lockerinstance):
    errmsg = ''
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
        #        minval, maxval = loadprogramminmax(lockerinstance, program)
                recipesarepresent = checkrecipes(lockerinstance, program)
                if not recipesarepresent:
                    errmsg = 'Program is invalid'
                break
        #with lockerinstance[0].lock:
        #    lockerinstance[0].program['startpos'] = minval
        #    lockerinstance[0].program['endpos'] = maxval
    if errmsg:
        ErrorEventWrite(lockerinstance, errmsg)
        return False
    else:
        return True

def CheckPositions(lockerinstance):
    result = CheckPiston(lockerinstance, 'Seal', 'Down')
    with lockerinstance[0].lock:
        result = result and lockerinstance[0].program['initialised']
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
        lockerinstance[0].robot['setpos'] = posnumber
        lockerinstance[0].robot['go'] = True

def ServoSetState(lockerinstance, state):
    with lockerinstance[0].lock:
        lockerinstance[0].servo[state] = True

def LaserSetState(lockerinstance, state):
    with lockerinstance[0].lock:
        lockerinstance[0].laser[state] = True

def Initialise(lockerinstance):
    with lockerinstance[0].lock:
        cycle = lockerinstance[0].program['cycle']
        lockerinstance[0].program['initialising'] = True
    if cycle == 0:
        #checking if seal piston is down
        sealdown = CheckPiston(lockerinstance, 'Seal', 'Down')
        if sealdown:
            with lockerinstance[0].lock:
                lockerinstance[0].program['cycle'] += 1
        else:
            SetPiston(lockerinstance, 'Seal', 'Down')
    if cycle == 1:
        #checking if robot is at home
        robothome = RobotState(lockerinstance, 'homepos')
        robotmoving = RobotState(lockerinstance, 'activecommand')
        if robothome:
            with lockerinstance[0].lock:
                lockerinstance[0].program['cycle'] += 1
        else:
            if not robotmoving:
                RobotGopos(lockerinstance, 0)
    if cycle == 2:
        #checking if servo is at home
        servopos = ServoState(lockerinstance, 'positionNumber')
        servomoving = ServoState(lockerinstance, 'moving')
        if servopos == 0:
            with lockerinstance[0].lock:
                lockerinstance[0].program['cycle'] += 1
        elif servopos == -1:
            if not servomoving:
                ServoSetState(lockerinstance, 'step')
        else:
            if not servomoving:
                ServoSetState(lockerinstance, 'homing')
    if cycle == 3:
        #checking if laser is ready
        LaserOn = LaserState(lockerinstance, 'LaserOn')
        LaserReady = LaserState(lockerinstance, 'LaserReady')
        LaserBusy = LaserState(lockerinstance, 'busy')
        LaserError = LaserState(lockerinstance, 'LaserError')
        ChillerError = LaserState(lockerinstance, 'ChillerError')
        if LaserReady and not LaserBusy:
            with lockerinstance[0].lock:
                lockerinstance[0].program['cycle'] += 1
        elif not LaserOn:
            LaserSetState(lockerinstance, 'LaserTurnOn')
        elif LaserBusy:
            ErrorEventWrite(lockerinstance, "Initialisation step 3: Laser Is Busy")
        elif LaserError or ChillerError:
            ErrorEventWrite(lockerinstance, "Initialisation step 3: Laser or Chiller Error")
        else:
            LaserSetState(lockerinstance, 'SetChannel')
    if cycle == 4:
        #checking scout
        StatusCheckCode = SCOUTState(lockerinstance, 'StatusCheckCode')
        if StatusCheckCode:
            with lockerinstance[0].lock:
                lockerinstance[0].program['cycle'] += 1
        else:
            LaserSetState(lockerinstance, 'SetChannel')
    if cycle == 5:
        with lockerinstance[0].lock:
            lockerinstance[0].program['cycle'] = 0
            lockerinstance[0].program['initialising'] = False
            lockerinstance[0].program['initialised'] = True 

def checkrecipes(lockerinstance, program):
    for line in program['Table']:
        recipe = line[RECIPE]
        if recipe:
            with lockerinstance[0].lock:
                path = lockerinstance[0].scout['recipesdir']
            if Path(path + recipe).is_file():
                continue
            else:
                return False
    return True

#def loadprogramminmax(lockerinstance, program):
#    minimum = reduce(lambda x,y: x[STEP] if x[STEP] <= y[STEP] else y[STEP], program['Table'])
#    maximum = reduce(lambda x,y: x[STEP] if x[STEP] >= y[STEP] else y[STEP], program['Table'])
#    return (minimum, maximum)

def loadprogramline(lockerinstance, program, number):
    #program dict with key table, where is list of lists of 9 elements each
    while True:
        result = []
        for programline in program['Table']:
            if programline[1] == number:
                result = programline
                break
        if result: break
        else: programline +=1
        with lockerinstance[0].lock:
            currentcycle = lockerinstance[0].program['cycle']
            maxintable = lockerinstance[0].program['endpos']
        if currentcycle >= maxintable: break
    return result

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
    program = programs['Programs'][programname]
    if cycle == 0: #table is from 1
        with lockerinstance[0].lock:
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
            endprogram(lockerinstance)
        else:
            programline = loadprogramline(lockerinstance, program, cycle)
            with lockerinstance[0].lock:
                progproxy['programline'] = programline

        

        
