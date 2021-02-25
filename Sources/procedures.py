

def startauto(lockerinstance):
    lockerinstance[0].lock.acquire()
    running = lockerinstance[0].program['running']
    lockerinstance[0].lock.release()
    if not running:
        lockerinstance[0].lock.acquire()
        lockerinstance[0].program['running'] = True
        lockerinstance[0].program['stepcomplete'] = False
        lockerinstance[0].program['stepnumber'] = 0
        lockerinstance[0].program['cycle'] = 0
        lockerinstance[0].lock.release()

def nextstep(lockerinstance):
    lockerinstance[0].lock.acquire()
    stepcomplete = lockerinstance[0].program['stepcomplete']
    lockerinstance[0].lock.release()
    if stepcomplete:
        lockerinstance[0].lock.acquire()
        lockerinstance[0].program['stepcomplete'] = False
        lockerinstance[0].program['stepnumber'] += 1
        lockerinstance[0].program['cycle'] = 0
        lockerinstance[0].lock.release()

def startprocedure(lockerinstance):
    lockerinstance[0].lock.acquire()
    step, auto = lockerinstance[0].program['stepmode'], lockerinstance[0].program['automode']
    lockerinstance[0].lock.release()
    if auto: startauto(lockerinstance)
    if step: nextstep(lockerinstance)

def CheckSafety(lockerinstance):
    return False

def CheckProgram(lockerinstance):
    return False

def CheckPositions(lockerinstance):
    return False

def CheckPiston(lockerinstance, pistonname, action):
    lockerinstance[0].lock.acquire()
    pistonState = lockerinstance[0].pistons['sensor' + pistonname + action]
    lockerinstance[0].lock.release()
    return pistonState

def RobotState(lockerinstance, state):
    lockerinstance[0].lock.acquire()
    robotstate = lockerinstance[0].robot[state]
    lockerinstance[0].lock.release()
    return robotstate

def ServoState(lockerinstance, state):
    lockerinstance[0].lock.acquire()
    servostate = lockerinstance[0].servo[state]
    lockerinstance[0].lock.release()
    return servostate

def SetPiston(lockerinstance, pistonname, action):
    lockerinstance[0].lock.acquire()
    lockerinstance[0].pistons[pistonname + action] = True
    lockerinstance[0].lock.release()

def RobotGopos(lockerinstance, posnumber):
    lockerinstance[0].lock.acquire()
    lockerinstance[0].robot['setpos'] = posnumber
    lockerinstance[0].robot['go'] = True
    lockerinstance[0].lock.release()

def ServoSetState(lockerinstance, state):
    lockerinstance[0].lock.acquire()
    lockerinstance[0].servo[state] = True
    lockerinstance[0].lock.release()

def Initialise(lockerinstance):
    lockerinstance[0].lock.acquire()
    cycle = lockerinstance[0].program['cycle']
    lockerinstance[0].program['initialising'] = True
    lockerinstance[0].lock.release()
    if cycle == 0:
        #checking if seal piston is down
        sealdown = CheckPiston(lockerinstance, 'Seal', 'Down')
        if sealdown:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].program['cycle'] += 1
            lockerinstance[0].lock.release()
        else:
            SetPiston(lockerinstance, 'Seal', 'Down')
    if cycle == 1:
        #checking if robot is at home
        robothome = RobotState(lockerinstance, 'homepos')
        robotmoving = RobotState(lockerinstance, 'activecommand')
        if robothome:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].program['cycle'] += 1
            lockerinstance[0].lock.release()
        else:
            if not robotmoving:
                RobotGopos(lockerinstance, 0)
    if cycle == 2:
        #checking if servo is at home
        servopos = ServoState(lockerinstance, 'positionNumber')
        servomoving = ServoState(lockerinstance, 'moving')
        if servopos == 0:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].program['cycle'] += 1
            lockerinstance[0].lock.release()
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
            lockerinstance[0].lock.acquire()
            lockerinstance[0].program['cycle'] += 1
            lockerinstance[0].lock.release()
        elif servopos == -1:
            if not servomoving:
                ServoSetState(lockerinstance, 'step')
        else:
            if not servomoving:
                ServoSetState(lockerinstance, 'homing')
    
    
    

