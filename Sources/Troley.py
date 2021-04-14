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
                with lockerinstance[0].lock:
                    lockerinstance[0].troley['Alive'] = self.Alive
                try:
                    self.loop(lockerinstance)
                except Exception as e:
                    ErrorEventWrite(lockerinstance, "Troley loop raised exception: "+ str(e))
            finally:
                with lockerinstance[0].lock:
                    self.Alive = lockerinstance[0].troley['Alive']
                    closeapp = lockerinstance[0].events['closeApplication']
                if closeapp: break

    def TroleyTrigger(self, lockerinstance):
        triggered = True
        for condition in self.config['TroleyTrigger']:
            with lockerinstance[0].lock:
                triggered &= lockerinstance[0].shared[condition['masterkey']][condition['key']]
        with lockerinstance[0].lock:
            lockerinstance[0].troley['push'] = triggered

    def loop(self, lockerinstance):
        while self.Alive:
            with lockerinstance[0].lock:
                dock, undock, rotate = lockerinstance[0].troley['dock'], lockerinstance[0].troley['undock'], lockerinstance[0].troley['rotate']
                lockerinstance[0].troley['dock'] = lockerinstance[0].troley['undock'] = lockerinstance[0].troley['rotate'] = False
                pistonsready = lockerinstance[0].pistons['Alive']
                servoready = lockerinstance[0].servo['Alive']
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
        with lockerinstance[0].lock:
            push = lockerinstance[0].troley['push']
            lockerinstance[0].troley['dockreleaseswitch'] = lockerinstance[0].GPIO[self.config['dockreleaseswitch']]
            lockerinstance[0].troley['docked'] = lockerinstance[0].GPIO[self.config['Docksensor']]
            if push:
                lockerinstance[0].troley['push'] = False
                if lockerinstance[0].troley['dockreleaseswitch']:
                    lockerinstance[0].troley['dock'] = True
                else:
                    lockerinstance[0].troley['undock'] = True
        try:
            self.getTroleynumber(lockerinstance)
        except Exception as e:
            with lockerinstance[0].lock:
                lockerinstance[0].troley['error'] = True
            ErrorEventWrite(lockerinstance, 'Trolley Number Read Failed\n' + str(e))

    def __parity(self, values = []):
        carry = True
        for value in values:
            carry ^= value
        return carry

    def getTroleynumber(self, lockerinstance):
        with lockerinstance[0].lock:
            bits = [lockerinstance[0].GPIO[bit] for bit in self.config['Troleynumberbits']]
            parity = lockerinstance[0].GPIO[self.config['Troleynumberparity']]
            docked = lockerinstance[0].troley['docked']
        if docked:
            if self.__parity([*bits, parity]):
                number = self.BitConverter(bits)
                with lockerinstance[0].lock:
                    lockerinstance[0].troley['number'] = number
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].troley['number'] = 'NA'

    def dockTroley(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].pistons[self.config['TroleyPistons']['dock']] = True

    def undockTroley(self, lockerinstance):
        with lockerinstance[0].lock:
            lockerinstance[0].pistons[self.config['TroleyPistons']['undock']] = True

    def rotatechamber(self, lockerinstance):
        with lockerinstance[0].lock:
            position = lockerinstance[0].servo['positionNumber']
            ready = lockerinstance[0].servo['iocoin']
        if position == -1 and ready:
            with lockerinstance[0].lock:
                lockerinstance[0].servo['homing'] = True
                lockerinstance[0].troley['rotate'] = True
        elif not ready:
            with lockerinstance[0].lock:
                lockerinstance[0].troley['rotate'] = True
        else:
            with lockerinstance[0].lock:
                lockerinstance[0].servo['step'] = True
