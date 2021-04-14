from threading import Thread, currentThread

def BlankFunc(*args, **kwargs): #Blank func to use as default value in function type parameter
    pass

def writeInLambda(variable, value): #Lambdas doesn't support appending
    variable = value
    return None

def dictKeyByVal(dict, byVal): #There is no default method to search for keys in dictionary by value
    keys = []
    items = dict.items()
    for item in items: #item = [key, value]
        if item[1] == byVal: keys.append(item[0])
    if len(keys) == 1:
        return keys[0]
    return keys

def ErrorEventWrite(lockerinstance, errstring = '', errorlevel = 255, noerror = False):
    with lockerinstance[0].lock:
        if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring + '\n'
        if not noerror:
            lockerinstance[0].errorlevel[errorlevel] = True
            lockerinstance[0].events['Error'] = True

class EventManager():
    def __init__(self, lockerinstance, input = '', edge = None, event = '', callback = BlankFunc, callbackargs = ()):
        self.backwardsrunning = False
        if not input:
            input = 'events.'
            if event and event[0] == '-':
                self.sign = True
                input += event[1:]
            else:
                input += event
            self.backwardsrunning = True
        if input and input[0] == '-':
            self.sign = True
            input = input[1:]
        else :
            self.sign = False
        if '.' in input:
            path = input.split('.')
            self.inputpath = lockerinstance[0].shared
            for i, branch in enumerate(path):
                if i >= len(path)-1: break
                self.inputpath = self.inputpath[branch]
            self.input = path[-1]
        else:
            self.inputpath = lockerinstance[0].GPIO
            self.input = input
        self.edge = edge
        self.callback = callback
        self.callbackargs = callbackargs
        self.event = event
        with lockerinstance[0].lock:
            self.state = self.inputpath[self.input]
            self.Alive = True
            self.name = currentThread().name
            lockerinstance[0].ect.append(self.name)
        self.loop(lockerinstance)

    def noedge(self, lockerinstance, currentstate):
        if not self.edge: 
            if (currentstate ^ self.sign):
                if self.event:
                    if not self.backwardsrunning:
                        with lockerinstance[0].lock:
                            lockerinstance[0].events[self.event] = True
                    return True
        return False
    
    def rising(self, lockerinstance, currentstate):
        if self.edge == 'rising':
            if self.state:
                with lockerinstance[0].lock:
                    self.state = self.inputpath[self.input]
            elif currentstate:
                if self.event:
                    if not self.backwardsrunning:
                        with lockerinstance[0].lock:
                            lockerinstance[0].events[self.event] = True
                    return True
        return False

    def falling(self, lockerinstance, currentstate):
        if self.edge == 'falling':
            if not self.state:
                with lockerinstance[0].lock:
                    self.state = self.inputpath[self.input]
            elif not currentstate:
                if self.event:
                    if not self.backwardsrunning:
                        with lockerinstance[0].lock:
                            lockerinstance[0].events[self.event] = True
                    return True
        return False

    def toggle(self, lockerinstance, currentstate):
        if self.edge == 'toggle':
            if self.state != currentstate:
                if self.event:
                    if not self.backwardsrunning:
                        with lockerinstance[0].lock:
                            lockerinstance[0].events[self.event] = True
                    return True
        return False

    def loop(self, lockerinstance):
        while True:
            with lockerinstance[0].lock:
                self.Alive = self.name in lockerinstance[0].ect and not lockerinstance[0].events['closeApplication']
                currentstate = self.inputpath[self.input]
            if not self.Alive: break
            args = (lockerinstance, currentstate)
            if any([self.noedge(*args), self.rising(*args), self.falling(*args), self.toggle(*args)]): break
        self.callback(*self.callbackargs)
        with lockerinstance[0].lock:
            if self.name in lockerinstance[0].ect: lockerinstance[0].ect.remove(self.name)
    
    @classmethod
    def AdaptEvent(cls, lockerinstance, input = '', edge = None, name = '', event = '', callback = BlankFunc, callbackargs = ()):
        evname = event if not name else name
        with lockerinstance[0].lock:
            ectActive = str('EventCatcher: ' + evname) in lockerinstance[0].ect
        if not ectActive:
            EventThread = Thread(target = cls, args = (lockerinstance, input, edge, event, callback, callbackargs))
            EventThread.setName('EventCatcher: ' + evname)
            EventThread.start()

    @classmethod
    def DestroyEvent(cls, lockerinstance, event = ''):
        eventname = 'EventCatcher: ' + event
        with lockerinstance[0].lock:
            ectActive = eventname in lockerinstance[0].ect
            if ectActive: lockerinstance[0].ect.remove(eventname)

class Bits():
    def __init__(self, len = 4, LE = False):
        self.le = LE
        self.len = len
        self.ones = 0
        for i in range(self.len):
            self.ones += pow(2,len-1-i)

    def IntToBitlist(self, integer = 0):
        integer &= self.ones
        result = []
        for i in range(self.len):
            power = pow(2,self.len-1-i)
            result.append(bool(integer//power))
            integer &= self.ones ^ power
        if not self.le:
            result = result[::-1]
        return result
    
    def BitListToInt(self, bitlist = [4*[False]]):
        if len(bitlist) > self.len:
            bitlist = bitlist[:self.len]
        elif len(bitlist) < self.len:
            bitlist.extend((self.len-len(bitlist))*[False])
        result = 0b0
        if self.le: bitlist = bitlist[::-1]
        for i, val in enumerate(bitlist):
            if val:
                result += pow(2,i)
        return result

    def Bits(self, values = [4*False]):
        result = None
        if isinstance(values, list):
            result = self.BitListToInt(values)
        elif isinstance(values, int):
            result = self.IntToBitlist(values)
        else:
            result = TypeError('Bits cannot be' + str(values))
        return result

    def __call__(self, values):
        return self.Bits(values)
            