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
            self.Alive = lockerinstance[0].program['automode']
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
        if running and not ready:
            control.Initialise(lockerinstance)

    def automode(self, lockerinstance):
        pass

    def stepmode(self, lockerinstance):
        pass