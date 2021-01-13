import tkinter as tk

class IOBar(tk.LabelFrame):
    def __init__(self, lockerinstance, elements = {}, relief=tk.GROOVE, bd=2, side = tk.LEFT, anchor = tk.W, master=None):
        self.master = master
        super().__init__(self.master)
        self.elements = elements.copy()
        self.locker = lockerinstance
        Frames = []
        currentFrame = self
        for i, key in enumerate(self.elements.keys()):
            if i//4 > len(Frames)-1:
                Frames.append(tk.Frame(master = self))
                currentFrame = Frames[i//4]
            if 'I' in key:
                self.configure(text='Robot Inputs')
                self.elements[key] =  tk.Canvas(currentFrame, bg='black', width = 20, height = 20)
                lblval = tk.StringVar()
                lblval.set(key)
                lbl = tk.Label(currentFrame, textvariable = lblval, width = 3)
                self.elements[key].pack(side = side, anchor = anchor, expand = tk.YES, fill=tk.BOTH)
                lbl.pack(side = side, anchor = anchor, expand = tk.YES, fill=tk.BOTH)
            else:
                self.configure(text='Robot Outputs')
                self.elements[key] = tk.BooleanVar()
                chk = tk.Checkbutton(currentFrame, text = key, width = 3 if not 'Changed' in key else 20, variable = self.elements[key], command = self.click)
                chk.pack(side = side, anchor = anchor, expand = tk.YES, fill=tk.BOTH)
        for frame in Frames:
            frame.pack(side=tk.TOP, expand=tk.YES)
             
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

class ScrolledTextbox(tk.LabelFrame):
    def __init__(self, lockerinstance, master = None, scrolltype = 'both', height=200, width=200):
        super().__init__(master = master, width = width, height = height)
        self.configure(text='Errors')
        self.master = master
        self.locker = lockerinstance
        self.text = tk.Text(self, height=height, width=width)
        if scrolltype in ('vertical','both'):
            self.vsb = tk.Scrollbar(self, orient='vertical', command = self.text.yview)#, yscrollcommand = lambda f, l, obj = self:obj.autoscroll(self.vsb, f, l))
            self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        else: self.vsb = None
        if scrolltype in ('horizontal','both'):
            self.hsb = tk.Scrollbar(self, orient='horizontal', command = self.text.xview)#, xscrollcommand = lambda f, l, obj = self:obj.autoscroll(self.hsb, f, l))
            self.hsb.pack(side=tk.BOTTOM, fill=tk.Y)
        else: self.Hsb = None
        self.text.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.text.pack(expand=tk.Y)
        self.vtext = ''

    def Update(self):
        self.locker[0].lock.acquire()
        text = self.locker[0].shared['Errors']
        self.locker[0].lock.release()
        if self.vtext != text:
            vpos, hpos = self.vsb.get(), self.hsb.get()
            prevw, prevh = self.text.winfo_width(), self.text.winfo_height()
            self.text.delete('1.0',tk.END)
            self.text.insert('1.0',text)
            
            wsub = prevw/self.text.winfo_width()
            hsub = prevh/self.text.winfo_height()
            self.text.xview_moveto(hpos[0]*wsub)
            self.text.yview_moveto(vpos[0]*hsub)
            self.vtext = text

class PistonControl(tk.Frame):
    def __init__(self, lockerinstance, elements = {}, relief=tk.GROOVE, bd=2, anchor = tk.NW, side =tk.TOP, master=None):
        self.locker = lockerinstance
        self.elements = elements
        self.master = master
        super().__init__(self.master)
        if 'Left' in self.elements.keys():
            self.buttonLeft = tk.Button(self)
            self.buttonLeft.config(highlightbackground= '#84bdac', borderwidth = 1, relief = 'ridge', activebackground='#f96348', background='#84bdac', justify='center', text='<--')
            self.buttonLeft.place(anchor='nw', height='30', width='30', x='0', y='0')
            self.buttonLeft.configure(command=self.Left)
        else:
            self.buttonLeft = tk.Canvas(self, bg='#74ad9c', borderwidth=1, relief = 'ridge', width = '30', height = '30')
            self.buttonLeft.place(anchor='nw', x='0', y='0')
        if 'Right' in self.elements.keys():
            self.buttonRight = tk.Button(self)
            self.buttonRight.config(highlightbackground= '#84bdac', borderwidth = 1, relief = 'ridge', activebackground='#f96348', background='#84bdac', justify='left', text='-->')
            self.buttonRight.place(anchor='nw', height='30', width='30', x='150', y='0')
            self.buttonRight.configure(command=self.Right)
        else:
            self.buttonRight = tk.Canvas(self, bg='#74ad9c', borderwidth=1, relief = 'ridge', width = '30', height = '30')
            self.buttonRight.place(anchor='nw', x='150', y='0')
        if 'Center' in self.elements.keys():
            self.buttonCenter = tk.Button(self)
            self.buttonCenter.config(highlightbackground= '#84bdac', borderwidth = 1, relief = 'ridge', activebackground='#f96348', background='#84bdac', text=self.elements['Center']['name'])
            self.buttonCenter.place(anchor='nw', height='30', width='120', x='30', y='0')
            self.buttonCenter.configure(command=self.Center)
        else:
            self.buttonCenter = tk.Canvas(self, bg='#74ad9c', borderwidth=1, relief = 'ridge', width = '120', height = '30')
            self.buttonCenter.place(anchor='nw', x='30', y='0')
        self.config(height='30', width='180')
    
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

class PistonBar(tk.LabelFrame):
    def __init__(self, lockerinstance, elements = [], relief=tk.GROOVE, bd=2, anchor = tk.W, side =tk.LEFT, master=None):
        self.master = master
        super().__init__(self.master)
        self.configure(text='Pneumatics')
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

class EstunBar(tk.LabelFrame):
    def __init__(self, lockerinstance, elements = {}, relief=tk.GROOVE, bd=2, anchor = tk.W, side =tk.LEFT, master=None):
        self.master = master
        super().__init__(self.master)
        self.configure(text='Servo')
        self.locker = lockerinstance
        self.elements = elements
        self.buttons = []
        for key in self.elements.keys():
            button = tk.Button(self, text='estun ' + key, command = lambda k = key: self.click(k)) 
            self.buttons.append(button)
        for btn in self.buttons:
            btn.configure(width = '30')
            btn.pack(expand = tk.YES, side=side, anchor = anchor)

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
        self.root = tk.Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.Wclose)
        self.checkbuttons = []
        self.variables = {}
        self.lastact = ''
        self.root.wm_title('debug window')
        self.textbox = ScrolledTextbox(self.locker, master = self.root, width = 100, height = 10)
        pistonbaritems = ['Seal', 'LeftPusher', 'RightPusher', 'ShieldingGas', 'HeadCooling', 'CrossJet', 'Air', 'Vacuum']
        estuncommands = ['homing', 'step', 'reset']
        self.locker[0].lock.acquire()
        self.IOFrame = tk.Frame(self.root)
        self.bars = [
            IOBar(self.locker, side = tk.LEFT, elements = dict(list(filter((lambda item: True if 'I' in item[0] else False), self.locker[0].GPIO.items()))), master = self.IOFrame),
            IOBar(self.locker, side = tk.LEFT, elements = dict(list(filter((lambda item: True if 'O' in item[0] else False), self.locker[0].GPIO.items()))), master = self.IOFrame)]
        self.locker[0].lock.release()
        self.bars.append(PistonBar(self.locker, side= tk.LEFT, elements = pistonbaritems, master = self.IOFrame))
        self.bars.append(EstunBar(self.locker, side= tk.TOP, elements = {item:None for item in estuncommands}, master = self.IOFrame))
        for bar in filter(lambda item:isinstance(item,EstunBar),self.bars):
            bar.pack(side=tk.LEFT, anchor = tk.NW)
        for bar in filter(lambda item:isinstance(item,IOBar),self.bars):
            bar.pack(side=tk.LEFT, anchor = tk.NW)
        for bar in filter(lambda item:isinstance(item,PistonBar),self.bars):
            bar.pack(side=tk.LEFT, anchor = tk.NW)
        self.IOFrame.grid(column=0, row=0, sticky=tk.W)
        self.textbox.grid(row=1)
        
        
        self.root.after(100,self.timerloop)

        while self.Alive:
            self.locker[0].lock.acquire()
            self.Alive = self.locker[0].console['Alive']
            self.locker[0].lock.release()
            self.root.update()
        #self.root.mainloop()
