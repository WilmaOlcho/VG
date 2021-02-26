

def startauto(lockerinstance):
    with lockerinstance[0].lock:
        running = lockerinstance[0].program['running']
        if not running:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].program['running'] = True
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
    return False

def CheckPositions(lockerinstance):
    return False

def CheckPiston(lockerinstance, pistonname, action):
    with lockerinstance[0].lock:
        pistonState = lockerinstance[0].pistons['sensor' + pistonname + action]
    return pistonState

def RobotState(lockerinstance, state):
    with lockerinstance[0].lock:
        robotstate = lockerinstance[0].robot[state]
    return robotstate

def ServoState(lockerinstance, state):
    with lockerinstance[0].lock:
        servostate = lockerinstance[0].servo[state]
    return servostate

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
    
    
    

