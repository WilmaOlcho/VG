from multiprocessing import Manager, Lock
from misc import BlankFunc

class SharedLocker(object):
    shared = None
    lock = None
    events = None
    errorlevel = None
    pistons = None
    safety = None
    estun = None
    mux = None
    estunModbus = None
    robot = None
    GPIO = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if SharedLocker.robot == None:
            SharedLocker.robot = Manager().dict({})
        if SharedLocker.GPIO == None:
            SharedLocker.GPIO = Manager().dict({})
        if SharedLocker.mux == None:
            SharedLocker.mux = Manager().dict({
                'busy':False,
                'ready':False,
                'onpath':False,
                'acquire':False,
                'release':False,
                'Alive':False})
        if SharedLocker.events == None:
            SharedLocker.events = Manager().dict({
                'ack':False,
                'Error':False,
                'RobotMoving':True,
                'ServoMoving':False,
                'anyButtonPressed':False,
                'EstunResetDone':False,
                'closeApplication':False})
        if SharedLocker.errorlevel == None:
            SharedLocker.errorlevel = Manager().dict({
                0:False,    1:False,    2:False,    3:False,    4:False,    5:False,    6:False,    7:False,    8:False,    9:False,    10:False,   11:False,   12:False,   13:False,   14:False,   15:False, 
                16:False,   17:False,   18:False,   19:False,   20:False,   21:False,   22:False,   23:False,   24:False,   25:False,   26:False,   27:False,   28:False,   29:False,   30:False,   31:False, 
                32:False,   33:False,   34:False,   35:False,   36:False,   37:False,   38:False,   39:False,   40:False,   41:False,   42:False,   43:False,   44:False,   45:False,   46:False,   47:False, 
                48:False,   49:False,   50:False,   51:False,   52:False,   53:False,   54:False,   55:False,   56:False,   57:False,   58:False,   59:False,   60:False,   61:False,   62:False,   63:False, 
                64:False,   65:False,   66:False,   67:False,   68:False,   69:False,   70:False,   71:False,   72:False,   73:False,   74:False,   75:False,   76:False,   77:False,   78:False,   79:False, 
                80:False,   81:False,   82:False,   83:False,   84:False,   85:False,   86:False,   87:False,   88:False,   89:False,   90:False,   91:False,   92:False,   93:False,   94:False,   95:False, 
                96:False,   97:False,   98:False,   99:False,   100:False,  101:False,  102:False,  103:False,  104:False,  105:False,  106:False,  107:False,  108:False,  109:False,  110:False,  111:False, 
                112:False,  113:False,  114:False,  115:False,  116:False,  117:False,  118:False,  119:False,  120:False,  121:False,  122:False,  123:False,  124:False,  125:False,  126:False,  127:False,  
                128:False,  129:False,  130:False,  131:False,  132:False,  133:False,  134:False,  135:False,  136:False,  137:False,  138:False,  139:False,  140:False,  141:False,  142:False,  143:False, 
                144:False,  145:False,  146:False,  147:False,  148:False,  149:False,  150:False,  151:False,  152:False,  153:False,  154:False,  155:False,  156:False,  157:False,  158:False,  159:False, 
                160:False,  161:False,  162:False,  163:False,  164:False,  165:False,  166:False,  167:False,  168:False,  169:False,  170:False,  171:False,  172:False,  173:False,  174:False,  175:False, 
                176:False,  177:False,  178:False,  179:False,  180:False,  181:False,  182:False,  183:False,  184:False,  185:False,  186:False,  187:False,  188:False,  189:False,  190:False,  191:False, 
                192:False,  193:False,  194:False,  195:False,  196:False,  197:False,  198:False,  199:False,  200:False,  201:False,  202:False,  203:False,  204:False,  205:False,  206:False,  207:False, 
                208:False,  209:False,  210:False,  211:False,  212:False,  213:False,  214:False,  215:False,  216:False,  217:False,  218:False,  219:False,  220:False,  221:False,  222:False,  223:False, 
                224:False,  225:False,  226:False,  227:False,  228:False,  229:False,  230:False,  231:False,  232:False,  233:False,  234:False,  235:False,  236:False,  237:False,  238:False,  239:False, 
                240:False,  241:False,  242:False,  243:False,  244:False,  245:False,  246:False,  247:False,  248:False,  249:False,  250:False,  251:False,  252:False,  253:False,  254:False,  255:False })
        if SharedLocker.pistons == None:
            SharedLocker.pistons = Manager().dict({
                'sealUp':False,
                'sealDown':False,
                'leftPusherFront':False,
                'leftPusherBack':False,
                'rightPusherFront':False,
                'rightPusherBack':False})
        if SharedLocker.safety == None:
            SharedLocker.safety = Manager().dict({
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
        if SharedLocker.estun == None:
            SharedLocker.estun = Manager().dict({
                'homing':False,
                'step':False,
                'DOG':False,
                'reset':False,
                'servoModuleFirstAccess':True,
                'Alive':True})
        if SharedLocker.estunModbus == None:
            SharedLocker.estunModbus = Manager().dict({
                'TGON':False,
                'SHOM':False,
                'PCON':False,
                'COIN':False
            })
        if SharedLocker.shared == None:
            SharedLocker.shared = Manager().dict({
                'Errors':'',
                'servoModuleFirstAccess':True,
                'configurationError':False,
                'TactWDT':False})
        if SharedLocker.lock == None:
            SharedLocker.lock = Lock()

    def WithLock(self, function, *args, **kwargs):
        self.lock.acquire()
        result = function(*args, **kwargs)
        self.lock.release()
        return result
