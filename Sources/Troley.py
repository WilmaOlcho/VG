import json
from Sources import ErrorEventWrite, Bits

class Troley(object):
    def __init__(self, lockerinstance, settingsfile = ''):
        while True:
            try:
                self.config = json.load(open(settingsfile))
            except Exception as e:
                ErrorEventWrite(lockerinstance, "Troley controller can't load json file\n" + str(e))
            else:
                self.BitConverter = Bits(len = 4)
                self.Alive = True
                lockerinstance[0].lock.acquire()
                lockerinstance[0].troley['Alive'] = self.Alive
                lockerinstance[0].lock.release()
                self.loop(lockerinstance)
            finally:
                lockerinstance[0].lock.acquire()
                self.Alive = lockerinstance[0].troley['Alive']
                closeapp = lockerinstance[0].events['closeApplication']
                lockerinstance[0].lock.release()
                if closeapp: break

    def TroleyTrigger(self, lockerinstance):
        triggered = True
        for condition in self.config['TroleyTrigger']:
            lockerinstance[0].lock.acquire()
            triggered &= lockerinstance[0].shared[condition['masterkey']][condition['key']]
            lockerinstance[0].lock.release()
        lockerinstance[0].lock.acquire()
        lockerinstance[0].troley['push'] = triggered
        lockerinstance[0].lock.release()

    def loop(self, lockerinstance):
        while self.Alive:
            lockerinstance[0].lock.acquire()
            dock, undock, rotate = lockerinstance[0].troley['dock'], lockerinstance[0].troley['undock'], lockerinstance[0].troley['rotate']
            lockerinstance[0].troley['dock'] = lockerinstance[0].troley['undock'] = lockerinstance[0].troley['rotate'] = False
            pistonsready = lockerinstance[0].pistons['Alive']
            servoready = lockerinstance[0].servo['Alive']
            lockerinstance[0].lock.release()
            if pistonsready:
                if dock: self.dockTroley(lockerinstance)
                if undock: self.undockTroley(lockerinstance)
            else:
                raise Exception('Pistons are not initialised')
            if servoready:
                if rotate: self.rotatechamber(lockerinstance)
            else:
                raise Exception('Servo is not initialised')
            self.statecontrol(lockerinstance)

    def statecontrol(self, lockerinstance):
        self.TroleyTrigger(lockerinstance)
        lockerinstance[0].lock.acquire()
        push = lockerinstance[0].troley['push']
        lockerinstance[0].troley['dockreleaseswitch'] = lockerinstance[0].GPIO[self.config['dockreleaseswitch']]
        lockerinstance[0].troley['docked'] = lockerinstance[0].GPIO[self.config['Docksensor']]
        if push:
            lockerinstance[0].troley['push'] = False
            if lockerinstance[0].troley['dockreleaseswitch']:
                lockerinstance[0].troley['dock'] = True
            else:
                lockerinstance[0].troley['undock'] = True
        lockerinstance[0].lock.release()
        try:
            self.getTroleynumber(lockerinstance)
        except Exception as e:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].troley['error'] = True
            lockerinstance[0].lock.release()
            ErrorEventWrite(lockerinstance, 'Trolley Number Read Failed\n' + str(e))

    def __parity(self, values = []):
        carry = True
        for value in values:
            carry ^= value
        return carry

    def getTroleynumber(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        bits = [lockerinstance[0].GPIO[bit] for bit in self.config['Troleynumberbits']]
        parity = lockerinstance[0].GPIO[self.config['Troleynumberparity']]
        docked = lockerinstance[0].troley['docked']
        lockerinstance[0].lock.release()
        if docked:
            if self.__parity([*bits, parity]):
                number = self.BitConverter(bits)
                lockerinstance[0].lock.acquire()
                lockerinstance[0].troley['number'] = number
                lockerinstance[0].lock.release()
        else:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].troley['number'] = 'NA'
            lockerinstance[0].lock.release()

    def dockTroley(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        lockerinstance[0].pistons[self.config['TroleyPistons']['dock']] = True
        lockerinstance[0].lock.release()

    def undockTroley(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        lockerinstance[0].pistons[self.config['TroleyPistons']['undock']] = True
        lockerinstance[0].lock.release()

    def rotatechamber(self, lockerinstance):
        lockerinstance[0].lock.acquire()
        position = lockerinstance[0].servo['positionNumber']
        ready = lockerinstance[0].servo['iocoin']
        lockerinstance[0].lock.release()
        if position == -1 and ready:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['homing'] = True
            lockerinstance[0].troley['rotate'] = True
            lockerinstance[0].lock.release()
        elif not ready:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].troley['rotate'] = True
            lockerinstance[0].lock.release()
        else:
            lockerinstance[0].lock.acquire()
            lockerinstance[0].servo['step'] = True
            lockerinstance[0].lock.release()