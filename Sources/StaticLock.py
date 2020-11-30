from multiprocessing import Manager, Lock

class SharedLocker(object):
    shared = None
    lock = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if SharedLocker.shared == None:
            SharedLocker.shared = Manager().dict({
                'Events':{
                    'ack':False,
                    'Error':False,
                    'RobotMoving':True,
                    'ServoMoving':False,
                    'anyButtonPressed':False},
                'Errorlevel':'',
                'Errors':'',
                'servoModuleFirstAccess':True,
                'configurationError':False,
                'TactWDT':False,
                'Pistons':{
                    'sealUp':False,
                    'sealDown':False,
                    'leftPusherFront':False,
                    'leftPusherBack':False,
                    'rightPusherFront':False,
                    'rightPusherBack':False},
                'Safety':{
                    'EstopArmed':False,
                    'EstopReleased':False,
                    'DoorOpen':False,
                    'DoorClosed':False,
                    'DoorLocked':False,
                    'TroleyInside':False,
                    'TroleySafe':False,
                    'THCPushed':False,
                    'ReleaseTroley':False,
                    'RobotError':False,
                    'LaserError':False,
                    'ServoError':False,
                    'sValve1Error':False,
                    'sValve2Error':False,
                    'ServoEDM':False,
                    'sValve1EDM':False,
                    'sValve2EDM':False,
                    'RobotEDM':False,
                    'LaserEDM':False,
                    'ZoneArmed':False,
                    'ZoneError':False,
                    'SafetyArmed':False,
                    'SafetyError':False,
                    'LockingJig':False},
                'Estun':{
                    'homing':False,
                    'step':False,
                    'DOG':False,
                    'reset':False}})
        if SharedLocker.lock == None:
            SharedLocker.lock = Lock()

    def WithLock(self, function, *args, **kwargs):
        SharedLocker.lock.acquire()
        result = function(*args, **kwargs)
        SharedLocker.lock.release()
        return result