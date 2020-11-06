from multiprocessing import Process, Manager, Lock
from time import sleep
from Estun import Estun



if __name__=="__main__":
    with Manager() as manager:
        shared = manager.dict({
            'Events':{
                'ack':False,
                'Error':False,
                'RobotMoving':False,
                'ServoMoving':False,
                'anyButtonPressed':False},
            'Error':255*[False],
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
                'LockingJig':False}
        })
        lock = Lock()
        processes = [
            Process(target = Estun.Run, args=(shared,lock)),
        ]
        for i in range(len(processes)):
            processes[i].start()
        for i in range(len(processes)):
            processes[i].join()
