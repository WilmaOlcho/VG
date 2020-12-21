from tkinter import *

class IOBar(Frame):
    def __init__(self, lockerinstance, elements = {}, relief=GROOVE, bd=2, side = LEFT, anchor = W, master=None):
        self.master = master
        super().__init__(self.master)
        self.elements = elements.copy()
        self.locker = {**lockerinstance}
        for key in self.elements.keys():
            self.elements[key] = BooleanVar()
        for key in self.elements.keys():
            chk = Checkbutton(self, text = key, variable = self.elements[key], command = self.click)
            chk.pack(side = side, anchor = anchor, expand = YES, fill=BOTH)
            
    def click(self):
        for key in self.elements.keys():
            self.locker[0].lock.acquire()
            if not self.locker[0].GPIO[key] == self.elements[key].get() and not 'I' in key:
                self.locker[0].GPIO[key] = self.elements[key].get()
            self.locker[0].lock.release()
    
class PistonBar(Frame):
    def __init__(self, lockerinstance, elements = {}, relief=GROOVE, bd=2, anchor = W, side =LEFT, master=None):
        self.master = master
        super().__init__(self.master)
        self.locker = {**lockerinstance}
        self.elements = elements
        self.frame={}
        for key in self.elements.keys():
            self.frame[key]=Frame(self)
            self.elements[key] = Canvas(self.frame[key], bg='black', width = 15, height = 15)
            btn = Button(self.frame[key], text=key, command = lambda k = key: self.click(k))
            self.elements[key].pack(side = LEFT, expand = YES)
            btn.pack(expand = YES, side=LEFT)
            self.frame[key].pack(expand = YES, anchor = anchor, side = side)

    def click(self, button):
        def toggle(boolvar):
            return not boolvar
        self.locker[0].lock.acquire()
        self.locker[0].pistons[button] = toggle(self.locker[0].pistons[button])
        self.locker[0].lock.release()

class EstunBar(Frame):
    def __init__(self, lockerinstance, elements = {}, relief=GROOVE, bd=2, anchor = W, side =LEFT, master=None):
        self.master = master
        super().__init__(self.master)
        self.locker = {**lockerinstance}
        self.elements = elements
        for key in self.elements.keys():
            btn = Button(self, text='estun ' + key, command = lambda k = key: self.click(k))
            btn.pack(expand = YES, side=LEFT)

    def click(self, button):
        def toggle(boolvar):
            return not boolvar
        self.locker[0].lock.acquire()
        self.locker[0].estun[button] = toggle(self.locker[0].estun[button])
        self.locker[0].lock.release()

class console(object):
    Alive = False

    def timerloop(self):
        self.locker[0].lock.acquire()
        for bar in self.bars:
            for key in bar.elements.keys():
                if isinstance(bar, PistonBar):
                    if 'sensor' + key in self.locker[0].pistons.keys():
                        bar.elements[key].configure(bg='green' if self.locker[0].pistons['sensor'+key] else 'black')
                elif isinstance(bar, EstunBar):
                    pass
                elif not self.locker[0].GPIO[key] == bar.elements[key].get():
                    bar.elements[key].set(self.locker[0].GPIO[key])
        self.textbox.delete('1.0',END)
        self.textbox.insert(INSERT,self.locker[0].shared['Errors'])
        self.locker[0].lock.release()
        self.root.after(300,self.timerloop)

    def __init__(self, locker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locker = {**locker}
        self.Alive = True
        self.root = Tk()
        self.locker[0].lock.acquire()
        self.checkbuttons = []
        self.variables = {}
        self.lastact = ''
        self.root.wm_title('debug window')
        self.textbox = Text(self.root, width = 90, height=10)
        pistonbaritems = ['SealUp', 'SealDown', 'LeftPusherFront', 'LeftPusherBack', 'RightPusherFront', 'RightPusherBack', 'ShieldingGas', 'HeadCooling', 'CrossJet']
        estuncommands = ['homing', 'step', 'reset']
        self.bars = [
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'I' in item[0] else False), self.locker[0].GPIO.items()))[:16]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'I' in item[0] else False), self.locker[0].GPIO.items()))[16:]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'O' in item[0] else False), self.locker[0].GPIO.items()))[:16]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'O' in item[0] else False), self.locker[0].GPIO.items()))[16:]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'ged' in item[0] else False), self.locker[0].GPIO.items()))), master = self.root)]
        for item in pistonbaritems:
            self.bars.append(PistonBar(self.locker, side= LEFT, elements = {item:None}, master = self.root))
        for item in estuncommands:
            self.bars.append(EstunBar(self.locker, side= LEFT, elements = {item:None}, master = self.root))
        for i, bar in enumerate(filter(lambda item:isinstance(item,PistonBar),self.bars)):
            bar.grid(column = 3, row = i )
        for i, bar in enumerate(filter(lambda item:isinstance(item,EstunBar),self.bars)):
            bar.grid(column = 4, row = i )
        for i, bar in enumerate(filter(lambda item:isinstance(item,IOBar),self.bars)):
            bar.grid(column = 0, row = i )
        self.textbox.grid(column = 0)
        
        self.locker[0].lock.release()
        self.root.after(100,self.timerloop)
        self.root.mainloop()