from tkinter import *

class IOBar(Frame):
    def __init__(self, lockerinstance, elements = {}, side = LEFT, anchor = W, master=None):
        self.master = master
        super().__init__(self.master)
        self.elements = elements.copy()
        self.locker = {**lockerinstance}
        for key in self.elements.keys():
            self.elements[key] = BooleanVar()
        for key in self.elements.keys():
            chk = Checkbutton(self, text = key, variable = self.elements[key], command = self.click)
            chk.pack(side = side, anchor = anchor, expand = YES)
            
    def click(self):
        for key in self.elements.keys():
            self.locker[0].lock.acquire()
            if not self.locker[0].GPIO[key] == self.elements[key].get() and not 'I' in key:
                self.locker[0].GPIO[key] = self.elements[key].get()
            self.locker[0].lock.release()
    
    #def timerloop(self):
    #    for key in self.elements.keys():
    #        self.locker[0].lock.acquire()
    #        if not self.locker[0].GPIO[key] == self.elements[key].get():
    #            self.elements[key].set(self.locker[0].GPIO[key])
    #        self.locker[0].lock.release()
    #    self.after(1000,self.timerloop)

class PistonBar(Frame):
    def __init__(self, lockerinstance, anchor = W, master=None):
        self.master = master
        super().__init__(self.master)
        self.locker = {**lockerinstance}
        self.elements = dict(self.locker[0].pistons.items())
        for key in self.elements.keys():
            self.elements[key] = BooleanVar()
        for key in self.elements.keys():
            chk = Label(self, text = key)
            chk.pack(side = LEFT, anchor = anchor, expand = YES)
            #btn = Button(self, text)

class console(object):
    Alive = False

    def timerloop(self):
        self.locker[0].lock.acquire()
        for bar in self.bars:
            for key in bar.elements.keys():
                if not self.locker[0].GPIO[key] == bar.elements[key].get():
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
        self.textbox.pack(side = BOTTOM)
        self.bars = [
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'I' in item[0] else False), self.locker[0].GPIO.items()))[:16]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'I' in item[0] else False), self.locker[0].GPIO.items()))[16:]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'O' in item[0] else False), self.locker[0].GPIO.items()))[:16]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'O' in item[0] else False), self.locker[0].GPIO.items()))[16:]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'ged' in item[0] else False), self.locker[0].GPIO.items()))), master = self.root)

        ]
        for bar in self.bars:
            bar.pack(fill=X)
            bar.config(relief=GROOVE, bd=2)
            #self.textbox.insert(END,str(self.locker[0].GPIO.items()[:15]))
        
        self.locker[0].lock.release()
        self.root.after(100,self.timerloop)
        self.root.mainloop()