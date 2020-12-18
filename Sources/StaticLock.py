from multiprocessing import Manager, Lock, Array, Value
from Sources.misc import BlankFunc

class BlankLocker(object):
    shared = {}
    lock = {}
    events = {}
    errorlevel = []
    pistons = {}
    safety = {}
    estun = {}
    mux = {}
    estunModbus = {}
    robot = {}
    console = {}
    GPIO = {}
    SICKGMOD = {}

class SharedLocker(object):
    def __init__(self, *args, **kwargs):
        self.shared = Manager().dict({
                'Errors':'',
                'servoModuleFirstAccess':True,
                'configurationError':False,
                'TactWDT':False})
        self.lock = Lock()
        self.attempts = Value('i',4)
        self.events = Manager().dict({
                'ack':False,
                'Error':False,
                'RobotMoving':True,
                'ServoMoving':False,
                'anyButtonPressed':False,
                'EstunResetDone':False,
                'closeApplication':False,
                'OutputChangedByRobot':False,
                'OutputsChangedByRobot':''})
        self.errorlevel = Array('b',255*[False])
        self.pistons = Manager().dict({
                'Alive':False,
                'SealUp':False,
                'SealDown':False,
                'sensorSealUp':False,
                'sensorSealDown':False,
                'LeftPusherFront':False,
                'LeftPusherBack':False,
                'sensorLeftPusherFront':False,
                'sensorLeftPusherBack':False,
                'RightPusherFront':False,
                'RightPusherBack':False,
                'sensorRightPusherFront':False,
                'sensorRightPusherBack':False,
                'sensorShieldingGasOk':False,
                'sensorAirOk':False,
                'sensorVacuumOk':False,
                'ShieldingGas':False,
                'HeadCooling':False,
                'CrossJet':False
                })
        self.safety = Manager().dict({
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
                'LockingJig':False})
        self.estun = Manager().dict({
                'homing':False,
                'step':False,
                'DOG':False,
                'reset':False,
                'servoModuleFirstAccess':True,
                'Alive':True})
        self.mux = Manager().dict({
                'busy':False,
                'ready':False,
                'onpath':False,
                'acquire':False,
                'release':False,
                'Alive':False})
        self.estunModbus = Manager().dict({
                'TGON':False,
                'SHOM':False,
                'PCON':False,
                'COIN':False
            })
        self.robot = Manager().dict({
                'Alive':False,
                'homepos':False,
                'homing':False,
                'go':False,
                'setoffset':False,
                'goonce':False,
                'setpos':0,
                'currentpos':0,
                'activecommand':False,
                'A':0.0,
                'X':0.0,
                'Y':0.0,
                'Z':0.0,
                'StatusRegister0':0,
                'StatusRegister1':0,
                'StatusRegister2':0,
                'StatusRegister3':0,
                'StatusRegister4':0,
                'StatusRegister5':0,
                'StatusRegister6':0})
        self.console = Manager().dict({
                'Alive':False
            })
        self.GPIO = Manager().dict({
                'somethingChanged':False,
                'I1':False, 'I2':False, 'I3':False, 'I4':False,
                'I5':False, 'I6':False, 'I7':False, 'I8':False,
                'I9':False, 'I10':False, 'I11':False, 'I12':False,
                'I13':False, 'I14':False, 'I15':False, 'I16':False,
                'I17':False, 'I18':False, 'I19':False, 'I20':False,
                'I21':False, 'I22':False, 'I23':False, 'I24':False,
                'I25':False, 'I26':False, 'I27':False, 'I28':False,
                'I29':False, 'I30':False, 'I31':False, 'I32':False,
                'O1':False, 'O2':False, 'O3':False, 'O4':False,
                'O5':False, 'O6':False, 'O7':False, 'O8':False,
                'O9':False, 'O10':False, 'O11':False, 'O12':False,
                'O13':False, 'O14':False, 'O15':False, 'O16':False,
                'O17':False, 'O18':False, 'O19':False, 'O20':False,
                'O21':False, 'O22':False, 'O23':False, 'O24':False,
                'O25':False, 'O26':False, 'O27':False, 'O28':False,
                'O29':False, 'O30':False, 'O31':False, 'O32':False})
        self.SICKGMOD0 = Manager().dict({
                'Alive':False
            })

