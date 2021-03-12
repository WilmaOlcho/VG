import json
import Sources.procedures as control
from Sources import EventManager

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
            #setting servo position
            if step == 2:
                with lockerinstance[0].lock:
                    if lockerinstance[0].servo['positionNumber'] == -1:
                        ErrorEventWrite(lockerinstance, 'servo is not ready')
                    if lockerinstance[0].servo['positionNumber'] == lockerinstance[0].program['programline'][control.SERVOPOS]
                        step += 1
                    else:
                        if not lockerinstance[0].servo['moving']:
                            lockerinstance[0].servo['step'] = True
            #setting robot position
            if step == 3:
                with lockerinstance[0].lock:
                    if lockerinstance[0].robot['setpos'] != lockerinstance[0].program['programline'][control.ROBOTPOS]
                        or lockerinstance[0].robot['settable'] != lockerinstance[0].program['programline'][control.ROBOTTABLE]:
                        lockerinstance[0].robot['settable'] = lockerinstance[0].program['programline'][control.ROBOTTABLE]
                        lockerinstance[0].robot['setpos'] = lockerinstance[0].program['programline'][control.ROBOTPOS]
                    else:
                        step += 1
            if step == 4:
                with lockerinstance[0].lock:
                    if lockerinstance[0].robot['currentpos'] != lockerinstance[0].program['programline'][control.ROBOTPOS]:
                        if not lockerinstance[0].robot['activecommand']:
                            lockerinstance[0].robot['go'] = True
                    else:
                        step += 1
            #align scout
            if step == 5:
                with lockerinstance[0].lock:
                    pass

        with lockerinstance[0].lock:
            lockerinstance[0].program['step'] = step





    def stepmode(self, lockerinstance):
        pass