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
    return keys

def ErrorEventWrite(lockerinstance, errstring = '', errorlevel = 255):
    lockerinstance[0].lock.acquire()
    if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring + '\n'
    lockerinstance[0].errorlevel[errorlevel] = True
    lockerinstance[0].events['Error'] = True
    lockerinstance[0].lock.release()

class EventManager():
    def __init__(self, lockerinstance, input = '', edge = None, event = ''):
        if input and input[0] == '-':
            self.sign = True
            input = input[1:]
        else :
            self.sign = False
        if '.' in input:
            path = input.split('.')
            evalstring = 'lockerinstance[0].' + path[:-1] + '["' + path[::-1][:1] + '"]'
            self.input = eval(evalstring)
        else:
            self.input = input
        self.edge = edge
        self.event = event
        lockerinstance[0].lock.acquire()
        self.state = lockerinstance[0].GPIO[self.input]
        self.Alive = lockerinstance[0].robot['Alive']
        self.name = currentThread().name
        lockerinstance[0].ect.append(self.name)
        lockerinstance[0].lock.release()
        self.loop(lockerinstance)

    def loop(self, lockerinstance):
        while self.Alive:
            lockerinstance[0].lock.acquire()
            self.Alive = lockerinstance[0].robot['Alive'] and self.name in lockerinstance[0].ect
            currentstate = bool(lockerinstance[0].GPIO[self.input])
            lockerinstance[0].lock.release()
            if not self.edge:
                if (currentstate ^ self.sign):
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].events[self.event] = True
                    lockerinstance[0].lock.release()
                    break
            elif self.edge == 'rising':
                if self.state:
                    lockerinstance[0].lock.acquire()
                    self.state = lockerinstance[0].GPIO[self.input]
                    lockerinstance[0].lock.release()
                elif currentstate:
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].events[self.event] = True
                    lockerinstance[0].lock.release()
                    break
            elif self.edge == 'falling':
                if not self.state:
                    lockerinstance[0].lock.acquire()
                    self.state = lockerinstance[0].GPIO[self.input]
                    lockerinstance[0].lock.release()
                elif not currentstate:
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].events[self.event] = True
                    lockerinstance[0].lock.release()
                    break
            elif self.edge == 'toggle':
                if self.state != currentstate:
                    lockerinstance[0].lock.acquire()
                    lockerinstance[0].events[self.event] = True
                    lockerinstance[0].lock.release()
                    break
        lockerinstance[0].lock.acquire()
        if self.name in lockerinstance[0].ect: lockerinstance[0].ect.remove(self.name)
        lockerinstance[0].lock.release()
    
    @classmethod
    def AdaptEvent(cls, lockerinstance, input = '', edge = None, event = ''):
        lockerinstance[0].lock.acquire()
        ectActive = str('EventCatcher: ' + event) in lockerinstance[0].ect
        lockerinstance[0].lock.release()
        if not ectActive:
            EventThread = Thread(target = cls, args = (lockerinstance, input, edge, event,))
            EventThread.setName('EventCatcher: ' + event)
            EventThread.start()

    @classmethod
    def DestroyEvent(cls, lockerinstance, event = ''):
        eventname = 'EventCatcher: ' + event
        lockerinstance[0].lock.acquire()
        ectActive = eventname in lockerinstance[0].ect
        if ectActive: lockerinstance[0].ect.remove(eventname)
        lockerinstance[0].lock.release()

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
        if isinstance(values, list):
            result = self.BitListToInt(values)
        elif isinstance(values, int):
            result = self.IntToBitlist(values)
        else:
            result = TypeError('Bits cannot be' + str(values))
        return result

    def __call__(self, values):
        self.Bits(values)

            