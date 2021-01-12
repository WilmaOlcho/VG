from tkinter import *
import tkinter as tk
from pygubu.widgets.tkscrollbarhelper import TkScrollbarHelper

class IOBar(Frame):
    def __init__(self, lockerinstance, elements = {}, relief=GROOVE, bd=2, side = LEFT, anchor = W, master=None):
        self.master = master
        super().__init__(self.master)
        self.elements = elements.copy()
        self.locker = {**lockerinstance}
        for key in self.elements.keys():
            if 'I' in key:
                self.elements[key] =  Canvas(self, bg='black', width = 15, height = 15)
                lblval = StringVar()
                lblval.set(key)
                lbl = Label(self, textvariable = lblval, width = 3)
                self.elements[key].pack(side = side, anchor = anchor, expand = YES, fill=BOTH)
                lbl.pack(side = side, anchor = anchor, expand = YES, fill=BOTH)
            else:
                self.elements[key] = BooleanVar()
        for key in self.elements.keys():
            if not 'I' in key:
                chk = Checkbutton(self, text = key, width = 3 if not 'Changed' in key else 20, variable = self.elements[key], command = self.click)
                chk.pack(side = side, anchor = anchor, expand = YES, fill=BOTH)
            
    def click(self):
        for key in self.elements.keys():
            self.locker[0].lock.acquire()
            if not self.locker[0].GPIO[key] == self.elements[key].get() and not 'I' in key:
                self.locker[0].GPIO[key] = self.elements[key].get()
            self.locker[0].lock.release()

    def Update(self):
        for key in self.elements.keys():
            self.locker[0].lock.acquire()
            if 'I' in key:
                self.elements[key].configure(bg='green' if self.locker[0].GPIO[key] else 'black')
            elif not self.locker[0].GPIO[key] == self.elements[key].get():
                self.elements[key].set(self.locker[0].GPIO[key])
            self.locker[0].lock.release()

class ScrolledTextbox(TkScrollbarHelper):
    def __init__(self, lockerinstance, master = None, scrolltype = 'both', height=200, width=200):
        super().__init__(master = master, width = width, height = height, scrolltype = scrolltype)
        self.locker = lockerinstance
        self.text = tk.Text(self.container)
        self.text.pack(expand='true', side='top', fill='both')
        self.add_child(self.text)

    def Update(self):
        self.text.delete('1.0',END)
        self.locker[0].lock.acquire()
        self.text.insert(INSERT,self.locker[0].shared['Errors'])
        self.locker[0].lock.release()

class PistonControl(Frame):
    def __init__(self, lockerinstance, elements = {}, relief=GROOVE, bd=2, anchor = NW, side =TOP, master=None):
        self.locker = lockerinstance
        self.elements = elements
        self.master = master
        super().__init__(self.master)
        if 'Left' in self.elements.keys():
            self.buttonLeft = tk.Button(self)
            self.buttonLeft.config(highlightbackground= '#84bdac', borderwidth = 1, relief = 'ridge', activebackground='#f96348', background='#84bdac', justify='center', text='<--')
            self.buttonLeft.place(anchor='nw', height='30', width='30', x='0', y='0')
            self.buttonLeft.configure(command=self.Left)
        if 'Right' in self.elements.keys():
            self.buttonRight = tk.Button(self)
            self.buttonRight.config(highlightbackground= '#84bdac', borderwidth = 1, relief = 'ridge', activebackground='#f96348', background='#84bdac', justify='left', text='-->')
            self.buttonRight.place(anchor='nw', height='30', width='30', x='80', y='0')
            self.buttonRight.configure(command=self.Right)
        if 'Center' in self.elements.keys():
            self.buttonCenter = tk.Button(self)
            self.buttonCenter.config(highlightbackground= '#84bdac', borderwidth = 1, relief = 'ridge', activebackground='#f96348', background='#84bdac', text=self.elements['Center']['name'])
            self.buttonCenter.place(anchor='nw', height='30', width='50', x='30', y='0')
            self.buttonCenter.configure(command=self.Center)
        self.config(height='30', width='110')
    
    def Left(self):
        self.locker[0].lock.acquire()
        self.locker[0].pistons[self.elements['Left']['coil']] = not self.locker[0].pistons[self.elements['Left']['coil']]
        self.locker[0].lock.release()

    def Right(self):
        self.locker[0].lock.acquire()
        self.locker[0].pistons[self.elements['Right']['coil']] = not self.locker[0].pistons[self.elements['Right']['coil']]
        self.locker[0].lock.release()

    def Center(self):
        self.locker[0].lock.acquire()
        if 'Right' in self.elements:
            if 'sensor' in self.elements['Right']: 
                self.locker[0].pistons[self.elements['Right']['coil']] = False
        if 'Left' in self.elements:
            if 'sensor' in self.elements['Left']: 
                self.locker[0].pistons[self.elements['Left']['coil']] = False
        self.locker[0].lock.release()


    def Update(self):
        self.locker[0].lock.acquire()
        if 'Left' in self.elements.keys():
            color = '#84bdac'
            if 'coil' in self.elements['Left']:
                if self.locker[0].pistons[self.elements['Left']['coil']]: color = '#f2fc45'
            if 'sensor' in self.elements['Left']:
                if self.locker[0].pistons[self.elements['Left']['sensor']]: color = '#ffdc45' if color == '#f2fc45' or color == '#ffdc45' else '#80ffaa'
            self.buttonLeft.configure(background = color)
        if 'Right' in self.elements.keys():
            color = '#84bdac'
            if 'coil' in self.elements['Right']:
                if self.locker[0].pistons[self.elements['Right']['coil']]: color = '#f2fc45'
            if 'sensor' in self.elements['Right']:
                if self.locker[0].pistons[self.elements['Right']['sensor']]: color = '#ffdc45' if color == '#f2fc45' or color == '#ffdc45' else '#80ffaa'
            self.buttonRight.configure(background = color)

        if 'Center' in self.elements.keys():
            if 'sensor' in self.elements['Center']:
                self.buttonCenter.configure(background = '#84ffac' if self.locker[0].pistons[self.elements['Center']['sensor']] else '#84bdac')
        self.locker[0].lock.release()

class PistonBar(Frame):
    def __init__(self, lockerinstance, elements = [], relief=GROOVE, bd=2, anchor = W, side =LEFT, master=None):
        self.master = master
        super().__init__(self.master)
        self.locker = lockerinstance
        self.controls = []
        self.elements = {}
        for item in elements:
            self.locker[0].lock.acquire()
            if item in self.locker[0].pistons.keys():
                if not item in self.elements:
                    self.elements[item] = {}
                self.elements[item]['Center'] = {'name':item}
                self.elements[item]['Right'] = {
                    'coil':item,
                    'sensor':item}
            if item + 'Up' in self.locker[0].pistons.keys():
                if not item in self.elements:
                    self.elements[item] = {}
                self.elements[item]['Center'] = {'name':item}
                self.elements[item]['Right'] = {
                    'coil':item + 'Up',
                    'sensor':'sensor' + item + 'Up'}
            if item + 'Down' in self.locker[0].pistons.keys():
                if not item in self.elements:
                    self.elements[item] = {}
                self.elements[item]['Center'] = {'name':item}
                self.elements[item]['Left'] = {
                    'coil':item + 'Down',
                    'sensor':'sensor' + item + 'Down'}
            if item + 'Front' in self.locker[0].pistons.keys():
                if not item in self.elements:
                    self.elements[item] = {}
                self.elements[item]['Center'] = {'name':item}
                self.elements[item]['Right'] = {
                    'coil':item + 'Front',
                    'sensor':'sensor' + item + 'Front'}
            if item + 'Back' in self.locker[0].pistons.keys():
                if not item in self.elements:
                    self.elements[item] = {}
                self.elements[item]['Center'] = {'name':item}
                self.elements[item]['Left'] = {
                    'coil':item + 'Back',
                    'sensor':'sensor' + item + 'Back'}
            if 'sensor' + item + 'Ok'in self.locker[0].pistons.keys():
                if not item in self.elements:
                    self.elements[item] = {}
                self.elements[item]['Center'] = {'sensor': 'sensor' + item + 'Ok', 'name' : item}
            self.locker[0].lock.release()
            if item in self.elements.keys():
                self.controls.append(PistonControl(lockerinstance, elements = self.elements[item], master = self))
        for piston in self.controls:
            piston.pack()

    def Update(self):
        for piston in self.controls: piston.Update()

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
    
    def Update(self):
        pass

class console(object):
    Alive = False

    def timerloop(self):
        for bar in self.bars:
            bar.Update()
        self.textbox.Update()
        self.root.after(300,self.timerloop)

    def Wclose(self):
        self.locker[0].lock.acquire()
        self.locker[0].events['closeApplication'] = True
        self.locker[0].lock.release()

    def __init__(self, locker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locker = {**locker}
        self.Alive = True
        self.locker[0].lock.acquire()
        self.locker[0].console['Alive'] = self.Alive
        self.locker[0].lock.release()
        self.root = Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.Wclose)
        self.checkbuttons = []
        self.variables = {}
        self.lastact = ''
        self.root.wm_title('debug window')
        self.textbox = ScrolledTextbox(self.locker, master = self.root, width = 250, height = 50)
        pistonbaritems = ['Seal', 'LeftPusher', 'RightPusher', 'ShieldingGas', 'HeadCooling', 'CrossJet', 'Air', 'Vacuum']
        estuncommands = ['homing', 'step', 'reset']
        self.locker[0].lock.acquire()
        self.bars = [
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'I' in item[0] else False), self.locker[0].GPIO.items()))[:16]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'I' in item[0] else False), self.locker[0].GPIO.items()))[16:]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'O' in item[0] else False), self.locker[0].GPIO.items()))[:16]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'O' in item[0] else False), self.locker[0].GPIO.items()))[16:]), master = self.root),
            IOBar(self.locker, elements = dict(list(filter((lambda item: True if 'ged' in item[0] else False), self.locker[0].GPIO.items()))), master = self.root)]
        self.locker[0].lock.release()
        self.bars.append(PistonBar(self.locker, side= LEFT, elements = pistonbaritems, master = self.root))
        for item in estuncommands:
            self.bars.append(EstunBar(self.locker, side= LEFT, elements = {item:None}, master = self.root))
        for i, bar in enumerate(filter(lambda item:isinstance(item,PistonBar),self.bars)):
            bar.grid(column = 3, row = i, sticky = W)
        for i, bar in enumerate(filter(lambda item:isinstance(item,EstunBar),self.bars)):
            bar.grid(column = 4, row = i, sticky = W)
        for i, bar in enumerate(filter(lambda item:isinstance(item,IOBar),self.bars)):
            bar.grid(column = 0, row = i, sticky = W)
        self.textbox.grid(column = 0)
        
        
        self.root.after(100,self.timerloop)

        while self.Alive:
            self.locker[0].lock.acquire()
            self.Alive = self.locker[0].console['Alive']
            self.locker[0].lock.release()
            self.root.update()
        #self.root.mainloop()