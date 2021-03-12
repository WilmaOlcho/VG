import json
import Sources.procedures as control
from Sources import EventManager, WDT, ErrorEventWrite
#

class programController(object):
    def __init__(self, lockerinstance, programfilepath, *args, **kwargs):
        self.Alive = True
        self.loop(lockerinstance)

    def loop(self, lockerinstance):
        with lockerinstance[0].lock:
            automode = lockerinstance[0].program['automode']
            stepmode = lockerinstance[0].program['stepmode']
            self.Alive = lockerinstance[0].program['Alive']
            automode = lockerinstance[0].program['automode']
        if automode: self.automode(lockerinstance)
        if stepmode: self.stepmode(lockerinstance)
        self.retrievestate(lockerinstance)

    def retrievestate(self, lockerinstance):
        with lockerinstance[0].lock:
            running = lockerinstance[0].program['running']
            lockerinstance[0].program['/running'] = not running
        safety = control.CheckSafety(lockerinstance)
        program = control.CheckProgram(lockerinstance)
        ready = control.CheckPositions(lockerinstance)
        if safety and program:
            EventManager.AdaptEvent(lockerinstance, input = 'events.startprogram', callback = control.startprocedure, callbackargs = (lockerinstance))
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].program['running'] = False
        if running:
            if not ready:
                control.Initialise(lockerinstance)
            else:
                control.Program(lockerinstance)


    def automode(self, lockerinstance):
        with lockerinstance[0].lock:
            running = lockerinstance[0].program['running']
            cycle = lockerinstance[0].program['cycle']
            cycleended = lockerinstance[0].program['cycleended']
            step = lockerinstance[0].program['step']
            lockerinstance[0].program['stepcomplete'] = False
        if running and cycle and not cycleended:
            #setting recipe for scout
            if step == 0:
                with lockerinstance[0].lock:
                    if lockerinstance[0].scout['recipe'] != lockerinstance[0].program['programline'][control.RECIPE]:
                        lockerinstance[0].scout['recipe'] = lockerinstance[0].program['programline'][control.RECIPE]
                    else:
                        step += 1
            if step == 1:
                with lockerinstance[0].lock:
                    if not lockerinstance[0].scout['Recipechangedsuccesfully']:
                        if not lockerinstance[0].events['KDrawWaitingForMessage']:
                            lockerinstance[0].scout['SetRecipe'] = True
                    else:
                        lockerinstance[0].scout['Recipechangedsuccesfully'] = False
                        step += 1
            #Setting seal down
            if step == 2:
                with lockerinstance[0].lock:
                    if not lockerinstance[0].pistons['sensorSealDown']:
                        lockerinstance[0].scout['SealDown'] = True
                    else:
                        step += 1
            #setting servo position
            if step == 3:
                with lockerinstance[0].lock:
                    if lockerinstance[0].servo['positionNumber'] == -1:
                        ErrorEventWrite(lockerinstance, 'servo is not ready')
                    if lockerinstance[0].servo['positionNumber'] == lockerinstance[0].program['programline'][control.SERVOPOS]:
                        step += 1
                    else:
                        if not lockerinstance[0].servo['moving']:
                            lockerinstance[0].servo['step'] = True
            #setting robot position
            if step == 4:
                with lockerinstance[0].lock:
                    if (lockerinstance[0].robot['setpos'] != lockerinstance[0].program['programline'][control.ROBOTPOS] or lockerinstance[0].robot['settable'] != lockerinstance[0].program['programline'][control.ROBOTTABLE]):
                        lockerinstance[0].robot['settable'] = lockerinstance[0].program['programline'][control.ROBOTTABLE]
                        lockerinstance[0].robot['setpos'] = lockerinstance[0].program['programline'][control.ROBOTPOS]
                    else:
                        step += 1
            if step == 5:
                with lockerinstance[0].lock:
                    if lockerinstance[0].robot['currentpos'] != lockerinstance[0].program['programline'][control.ROBOTPOS]:
                        if not lockerinstance[0].robot['activecommand']:
                            lockerinstance[0].robot['go'] = True
                    else:
                        step += 1
            #Setting seal up
            if step == 6:
                with lockerinstance[0].lock:
                    if lockerinstance[0].pistons['sensorSealDown']:
                        lockerinstance[0].scout['SealUp'] = True
                    else:
                        step += 1
            #Wait 3s until sealing were perfect
            if step == 7:
                def exceed(lockerinstance = lockerinstance):
                    with lockerinstance[0].lock:
                        lockerinstance[0].program['step'] += 1 
                WDT(lockerinstance, additionalFuncOnExceed = exceed, noerror = True, limit = 3, scale = 's')
            #align scout
            if step == 8:
                with lockerinstance[0].lock:
                    lockerinstance[0].scout['ManualAlignPage'] = lockerinstance[0].program['programline'][control.PAGE]
                    if not lockerinstance[0].events['KDrawWaitingForMessage']:
                        lockerinstance[0].scout['ManualAlign'] = True
                    if lockerinstance[0].scout['ManualAlignCheck']:
                        lockerinstance[0].scout['ManualAlignCheck'] = False
                        step +=1
            #SCOUT weld
            if step == 9:
                with lockerinstance[0].lock:
                    lockerinstance[0].scout['ManualWeldPage'] = lockerinstance[0].program['programline'][control.PAGE]
                    if not lockerinstance[0].events['KDrawWaitingForMessage']:
                        lockerinstance[0].scout['ManualWeld'] = True
                    if lockerinstance[0].scout['ManualWeldCheck']:
                        lockerinstance[0].scout['ManualWeldCheck'] = False
                        step +=1
            if step == 10:
                with lockerinstance[0].lock:
                    lockerinstance[0].program['cycleended'] = True
                    step = 0
        with lockerinstance[0].lock:
            if lockerinstance[0].program['step'] < step:
                lockerinstance[0].program['step'] = step

    def stepmode(self, lockerinstance):
        with lockerinstance[0].lock:
            running = lockerinstance[0].program['running']
            cycle = lockerinstance[0].program['cycle']
            cycleended = lockerinstance[0].program['cycleended']
            step = lockerinstance[0].program['step']
        if running and cycle and not cycleended:
            with lockerinstance[0].lock: #locking whole method for event-compatibility
                #setting recipe for scout
                if step == 0:
                    if lockerinstance[0].scout['recipe'] != lockerinstance[0].program['programline'][control.RECIPE]:
                        lockerinstance[0].scout['recipe'] = lockerinstance[0].program['programline'][control.RECIPE]
                    else:
                        lockerinstance[0].program['stepcomplete'] = True
                if step == 1:
                    if not lockerinstance[0].scout['Recipechangedsuccesfully']:
                        if not lockerinstance[0].events['KDrawWaitingForMessage']:
                            lockerinstance[0].scout['SetRecipe'] = True
                    else:
                        lockerinstance[0].scout['Recipechangedsuccesfully'] = False
                        step += 1
                #Setting seal down
                if step == 2:
                    if not lockerinstance[0].pistons['sensorSealDown']:
                        lockerinstance[0].scout['SealDown'] = True
                    else:
                        lockerinstance[0].program['stepcomplete'] = True
                #setting servo position
                if step == 3:
                    if lockerinstance[0].servo['positionNumber'] == -1:
                        ErrorEventWrite(lockerinstance, 'servo is not ready')
                    if lockerinstance[0].servo['positionNumber'] == lockerinstance[0].program['programline'][control.SERVOPOS]:
                        step += 1
                    else:
                        if not lockerinstance[0].servo['moving']:
                            lockerinstance[0].servo['step'] = True
                #setting robot position
                if step == 4:
                    if lockerinstance[0].robot['setpos'] != lockerinstance[0].program['programline'][control.ROBOTPOS] or lockerinstance[0].robot['settable'] != lockerinstance[0].program['programline'][control.ROBOTTABLE]:
                        lockerinstance[0].robot['settable'] = lockerinstance[0].program['programline'][control.ROBOTTABLE]
                        lockerinstance[0].robot['setpos'] = lockerinstance[0].program['programline'][control.ROBOTPOS]
                    else:
                        lockerinstance[0].program['stepcomplete'] = True
                if step == 5:
                    if lockerinstance[0].robot['currentpos'] != lockerinstance[0].program['programline'][control.ROBOTPOS]:
                        if not lockerinstance[0].robot['activecommand']:
                            lockerinstance[0].robot['go'] = True
                    else:
                        lockerinstance[0].program['stepcomplete'] = True
                #Setting seal up
                if step == 6:
                    if lockerinstance[0].pistons['sensorSealDown']:
                        lockerinstance[0].scout['SealUp'] = True
                    else:
                        lockerinstance[0].program['stepcomplete'] = True
            #Wait 3s until sealing were perfect
            if step == 7:
                def exceed(lockerinstance = lockerinstance):
                    with lockerinstance[0].lock:
                        lockerinstance[0].program['stepcomplete'] = True
                WDT(lockerinstance, additionalFuncOnExceed = exceed, noerror = True, limit = 3, scale = 's')
            with lockerinstance[0].lock:
                #align scout
                if step == 8:
                    lockerinstance[0].scout['ManualAlignPage'] = lockerinstance[0].program['programline'][control.PAGE]
                    if not lockerinstance[0].events['KDrawWaitingForMessage']:
                        lockerinstance[0].scout['ManualAlign'] = True
                    if lockerinstance[0].scout['ManualAlignCheck']:
                        lockerinstance[0].scout['ManualAlignCheck'] = False
                        lockerinstance[0].program['stepcomplete'] = True
                #SCOUT weld
                if step == 9:
                    lockerinstance[0].scout['ManualWeldPage'] = lockerinstance[0].program['programline'][control.PAGE]
                    if not lockerinstance[0].events['KDrawWaitingForMessage']:
                        lockerinstance[0].scout['ManualWeld'] = True
                    if lockerinstance[0].scout['ManualWeldCheck']:
                        lockerinstance[0].scout['ManualWeldCheck'] = False
                        lockerinstance[0].program['stepcomplete'] = True
                if step == 10:
                    lockerinstance[0].program['cycleended'] = True
