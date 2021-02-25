import json
import Sources.procedures as control
from Sources import EventManager

class programController(object):
    def __init__(self, lockerinstance, programfilepath, *args, **kwargs):
        self.Alive = True
        self.loop(lockerinstance)

    def loop(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        automode = lockerinstance[0].program['automode']
        stepmode = lockerinstance[0].program['stepmode']
        self.Alive = lockerinstance[0].program['automode']
        automode = lockerinstance[0].program['automode']
        lockerinstance[0].lock.release()
        if automode: self.automode(lockerinstance)
        if stepmode: self.stepmode(lockerinstance)

        self.retrievestate(lockerinstance)

    def retrievestate(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        running = lockerinstance[0].program['running']
        lockerinstance[0].program['/running'] = not running
        lockerinstance[0].lock.release()
        safety = control.CheckSafety(lockerinstance)
        program = control.CheckProgram(lockerinstance)
        ready = control.CheckPositions(lockerinstance)
        if safety and program:
            EventManager.AdaptEvent(lockerinstance, input = 'events.startprogram', callback = control.startprocedure, callbackargs = (lockerinstance))
        else:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].program['running'] = False
            lockerinstance[0].lock.release()
        if running and not ready:
            control.Initialise(lockerinstance)

    def automode(self, lockerinstance):
        pass

    def stepmode(self, lockerinstance):
        pass