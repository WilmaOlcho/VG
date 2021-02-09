import tkinter as tk
from tkinter import ttk
from Variables import Variables

class SettingsScreen(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.master = master
        self.name = 'Ustawienia i tryb ręczny'
        self.miscpneumaticsframe = tk.LabelFrame(master = self, text = 'Osłony pneumatyczne')
        self.widgets = [
            Troley(self, text = 'Wózek'),
            PistonControl(master = self.miscpneumaticsframe, variables = self.variables, buttontext = 'Gaz osłonowy', masterkey = 'pistoncontrol', key = 'shieldinggas'),
            PistonControl(master = self.miscpneumaticsframe, variables = self.variables, buttontext = 'Nóż powietrzny', masterkey = 'pistoncontrol', key = 'crossjet'),
            PistonControl(master = self.miscpneumaticsframe, variables = self.variables, buttontext = 'Chłodzenie głowicy', masterkey = 'pistoncontrol', key = 'headcooling'),
            self.miscpneumaticsframe
                    ]
        for widget in self.widgets:
            if isinstance(widget, tk.LabelFrame):
                widget.pack(side = tk.LEFT, anchor = tk.NW)
            else:
                widget.pack(anchor = tk.NW)
        self.pack()
    
    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class Troley(tk.LabelFrame):
    def __init__(self, master = None, variables = Variables(), text = 'text'):
        super().__init__(master = master, text = text)
        self.variables = variables
        self.master = master
        self.pistonlabeledFrame = tk.LabelFrame(self, text = 'Siłowniki')
        self.widgets = [
            ServoControl(master = self, text = 'Serwo', variables = self.variables, buttons = self.variables['servocontrol']['buttons'], lamps = self.variables['servocontrol']['lamps']),
            PistonControl(master = self.pistonlabeledFrame, variables = self.variables, buttontext = 'Siłowniki wózka', masterkey = 'pistoncontrol', key = 'pusher'),
            PistonControl(master = self.pistonlabeledFrame, variables = self.variables, buttontext = 'Siłownik uszczelnienia', masterkey = 'pistoncontrol', key = 'seal'),
            self.pistonlabeledFrame
                    ]
        for widget in self.widgets:
            widget.pack(anchor = tk.NW)
        self.pack()
    
    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class ServoControl(tk.LabelFrame):
    def __init__(self, master = None, text = '', variables = Variables(),  buttons = {}, lamps = {}):
        super().__init__(master = master, text = text)
        self.variables = variables
        self.master = master
        self.buttonsframe = tk.Frame(self)
        self.lampsframe = tk.Frame(self)
        self.widgets = [self.buttonsframe, self.lampsframe]
        for key, value in buttons.items():
            self.widgets.append(TroleyButton(self.buttonsframe, text = key, variables = self.variables, masterkey = 'troley', key = value, width = 25, height = 2))
        for key, value in lamps.items():
            self.widgets.append(TroleyLamp(self.lampsframe, text = key, variables = self.variables, masterkey = 'troley', key = value, width = 40, height = 40))
        
        for widget in self.widgets:
            if widget.master == self:
                widget.pack(side = tk.LEFT, anchor = tk.W)
            else:
                widget.pack(anchor = tk.N)
        self.pack()
    
    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class TroleyButton(tk.Button):
    def __init__(self, master = None, variables = Variables(), masterkey = '', text = '', key = '', width = 25, height = 3):
        super().__init__(master = master, text = text, command = self.click, width = width, height = height)
        self.key = key
        self.variables = variables
        self.master = master
        self.masterkey = masterkey

    def click(self):
        if self.key[0] == '-':
            self.variables[self.masterkey][self.key[1:]] = False
        else:
            self.variables[self.masterkey][self.key] = True

    def update(self):
        super().update()

class TroleyLamp(tk.Frame):
    def __init__(self, master = None, text = '', variables = Variables(), masterkey = '', key = '', width = 25, height = 3):
        super().__init__(master = master, relief = 'ridge', borderwidth = 2)
        self.lamp = tk.Canvas(master = self, width = width, height = height)
        self.caption = tk.Label(master = self, text = text, width = 19)
        self.caption.pack(side = tk.LEFT)
        self.lamp.pack(side = tk.LEFT)
        self.key = key
        self.variables = variables
        self.master = master
        self.masterkey = masterkey
        self.lit = False

    def update(self):
        super().update()
        if self.key[0] == '-':
            self.lit = not self.variables[self.masterkey][self.key[1:]]
        else:
            self.lit = self.variables[self.masterkey][self.key]
        self.lamp.config(bg = 'green' if self.lit else 'black')

class PistonControl(tk.Frame):
    def __init__(self, master = None, masterkey = 'pistoncontrol', key = '', variables = Variables(), buttontext = '', width = 25, height = 3):
        super().__init__(master = master)
        self.variables = variables
        self.elements = self.variables[masterkey][key]
        self.master = master
        self.masterkey = masterkey,
        self.key = key
        if 'Left' in self.elements.keys():
            self.buttonLeft = tk.Button(self)
            self.buttonLeft.config(highlightbackground= '#84bdac', borderwidth = 1, relief = 'ridge', activebackground='#f96348', background='#84bdac', justify='center', text='<--')
            self.buttonLeft.place(anchor='nw', height='90', width='90', x='0', y='0')
            self.buttonLeft.configure(command=self.Left)
        else:
            self.buttonLeft = tk.Canvas(self, bg='#74ad9c', borderwidth=1, relief = 'ridge', width = '90', height = '90')
            self.buttonLeft.place(anchor='nw', x='0', y='0')
        if 'Right' in self.elements.keys():
            self.buttonRight = tk.Button(self)
            self.buttonRight.config(highlightbackground= '#84bdac', borderwidth = 1, relief = 'ridge', activebackground='#f96348', background='#84bdac', justify='left', text='-->')
            self.buttonRight.place(anchor='nw', height='90', width='90', x='270', y='0')
            self.buttonRight.configure(command=self.Right)
        else:
            self.buttonRight = tk.Canvas(self, bg='#74ad9c', borderwidth=4, relief = 'ridge', width = '90', height = '90')
            self.buttonRight.place(anchor='nw', x='270', y='0')
        if 'Center' in self.elements.keys():
            self.buttonCenter = tk.Button(self)
            self.buttonCenter.config(highlightbackground= '#84bdac', borderwidth = 1, relief = 'ridge', activebackground='#f96348', background='#84bdac', text=buttontext)
            self.buttonCenter.place(anchor='nw', height='90', width='180', x='90', y='0')
            self.buttonCenter.configure(command=self.Center)
        else:
            self.buttonCenter = tk.Canvas(self, bg='#74ad9c', borderwidth=1, relief = 'ridge', width = '180', height = '90')
            self.buttonCenter.place(anchor='nw', x='90', y='0')
        self.config(height='90', width='360')
        self.pack()

    def Left(self):
        self.elements['Left']['coil'] = not self.elements['Left']['coil']
        if 'Right' in self.elements:
            if 'sensor' in self.elements['Right']: 
               self.elements['Right']['coil'] = False

    def Right(self):
        self.elements['Right']['coil'] = not self.elements['Right']['coil']
        if 'Left' in self.elements:
            if 'sensor' in self.elements['Left']: 
                self.elements['Left']['coil'] = False
        
    def Center(self):
        if 'Right' in self.elements:
            self.elements['Right']['coil'] = False
        if 'Left' in self.elements:
            self.elements['Left']['coil'] = False
        
    def update(self):
        super().update()
        if 'Left' in self.elements.keys():
            color = '#84bdac'
            bd = 1
            if 'coil' in self.elements['Left']:
                if self.elements['Left']['coil']: color = '#f2fc45'
            if 'sensor' in self.elements['Left']:
                if self.elements['Left']['sensor']: 
                    color = '#ffdc45' if color == '#f2fc45' or color == '#ffdc45' else '#80ffaa'
                    bd = 8
                else: bd = 1
            self.buttonLeft.configure(background = color, borderwidth = bd)
        if 'Right' in self.elements.keys():
            color = '#84bdac'
            bd = 1
            if 'coil' in self.elements['Right']:
                if self.elements['Right']['coil']: color = '#f2fc45'
            if 'sensor' in self.elements['Right']:
                if self.elements['Right']['sensor']: 
                    color = '#ffdc45' if color == '#f2fc45' or color == '#ffdc45' else '#80ffaa'
                    bd = 8
                else: bd = 1
            self.buttonRight.configure(background = color, borderwidth = bd)
        if 'Center' in self.elements.keys():
            if 'sensor' in self.elements['Center']:
                self.buttonCenter.configure(background = '#84ffac' if self.elements['Center']['sensor'] else '#84bdac')
        
