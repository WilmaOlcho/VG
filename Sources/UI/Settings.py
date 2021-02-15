import tkinter as tk
from tkinter import ttk
from Variables import Variables
from Widgets.callableFont import Font
from getroot import getroot

class SettingsScreen(dict):
    def __init__(self, master = None, variables = Variables()):
        self.frame = ttk.Frame(master = master)
        self.settings = master.settings['SettingsScreen']
        self.frame.__setattr__('settings',self.settings)
        self.root = getroot(master)
        self.font = self.root.font
        self.name = self.settings['Name']
        self.miscpneumaticsframe = ttk.LabelFrame(master = self.frame, text = self.settings["Pneumatics"]['Label'])
        self.miscpneumaticsframe.__setattr__('settings', self.settings['Pneumatics'])
        self.widgets = [
            Troley(self.frame),
            PistonControl(master = self.miscpneumaticsframe, button = 'ShieldingGas'),
            PistonControl(master = self.miscpneumaticsframe, button = 'CrossJet'),
            PistonControl(master = self.miscpneumaticsframe, button = 'HeadCooling'),
            self.miscpneumaticsframe
        ]
        for widget in self.widgets:
            if isinstance(widget, ttk.LabelFrame):
                widget.pack(side = tk.LEFT, anchor = tk.NW)
            else:
                widget.pack(anchor = tk.NW)
        self.frame.pack(expand = tk.YES, fill=tk.BOTH)
    
    def update(self):
        self.frame.update()
        for widget in self.widgets:
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class Troley(dict):
    def __init__(self, master = None):
        super().__init__()
        self.root = getroot(master)
        self.settings = master.settings['Troley']
        self.font = self.root.font
        self.frame = ttk.LabelFrame(master = master, text = self.settings['Label'])
        self.frame.__setattr__('settings', self.settings)
        self.pistonlabeledFrame = ttk.LabelFrame(self.frame, text = self.settings['Pneumatics']['Label'])
        self.pistonlabeledFrame.__setattr__('settings', self.settings['Pneumatics'])
        self.widgets = [
            ServoControl(master = self.frame, buttons = self.root.variables['servocontrol']['buttons'], lamps = self.root.variables['servocontrol']['lamps']),
            self.pistonlabeledFrame
                    ]
        for piston in self.settings['Pneumatics']:
            if piston == 'Label': continue
            PistonControl(master = self.pistonlabeledFrame, button=piston)
        for widget in self.widgets:
            widget.pack(anchor = tk.NW)
        self.frame.pack()
    
    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class ServoControl(dict):
    def __init__(self, master = None, buttons = {}, lamps = {}):
        super().__init__()
        self.root = getroot(master)
        self.font = self.root.font
        self.settings = master.settings['Servo']
        self.frame = ttk.LabelFrame(master = master, text = self.settings['Label'])
        self.frame.__setattr__('settings',self.settings)
        self.master = master
        self.buttonsframe = tk.Frame(self.frame)
        self.buttonsframe.__setattr__('settings', self.settings)
        self.lampsframe = tk.Frame(self.frame)
        self.lampsframe.__setattr__('settings', self.settings)
        self.widgets = [self.buttonsframe, self.lampsframe]
        for key, value in buttons.items():
            self.widgets.append(TroleyButton(self.buttonsframe, text = key, key = value))
        for key, value in lamps.items():
            self.widgets.append(TroleyLamp(self.lampsframe, text = key, key = value))
        
        for widget in self.widgets:
            if widget.master == self:
                widget.frame.pack(side = tk.LEFT, anchor = tk.W)
            else:
                widget.pack(anchor = tk.N)
        self.frame.pack()
    
    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class TroleyButton(dict):
    def __init__(self, master = None, text = '', key = ''):
        super().__init__()
        self.root = getroot(master)
        self.font = self.root.font
        self.settings = master.settings['Button']
        self.frame = tk.Button(master = master, font = self.font(), text = text, command = self.click, width = self.settings['width'], height = self.settings['height'])
        self.frame.__setattr__('settings',self.settings)
        self.key = key
        self.master = master
        self.masterkey = self.settings['masterkey']

    def click(self):
        if self.key[0] == '-':
            self.root.variables[self.masterkey][self.key[1:]] = False
        else:
            self.root.variables[self.masterkey][self.key] = True

    def update(self):
        super().update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class TroleyLamp(dict):
    def __init__(self, master = None, text = '', key = ''):
        super().__init__()
        self.root = getroot(master)
        self.font = self.root.font
        self.settings = master.settings['Lamp']
        self.frame = tk.Frame(master, **self.settings['frame'])
        self.frame.__setattr__('settings',self.settings)
        self.lamp = tk.Canvas(master = self.frame, width = self.settings['width'], height = self.settings['height'])
        self.caption = ttk.Label(master = self.frame, text = text, **self.settings['caption'])
        self.key = key
        self.master = master
        self.masterkey = self.settings['masterkey']
        self.caption.pack(side = tk.LEFT)
        self.lamp.pack(side = tk.LEFT)
        self.lit = False

    def update(self):
        super().update()
        if self.key[0] == '-':
            self.lit = not self.root.variables[self.masterkey][self.key[1:]]
        else:
            self.lit = self.root.variables[self.masterkey][self.key]
        self.lamp.config(bg = self.settings['Color']['active'] if self.lit else self.settings['Color']['normal'])

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class PistonControl(dict):
    def __init__(self, master = None, button = "", **kwargs):
        super().__init__()
        self.frame = tk.Frame(master = master)
        self.settings = master.settings[button]
        self.frame.__setattr__('settings',self.settings)
        self.root = getroot(master)
        self.elements = self.root.variables[self.settings['masterkey']][self.settings['key']]
        self.font = self.root.font
        config = self.root.settings['widget']['pistonbutton']
        if 'Left' in self.elements.keys():
            self.buttonLeft = tk.Button(self.frame, font = self.font())
            self.buttonLeft.config(**config['Left']['Button'])
            self.buttonLeft.configure(command=self.Left)
        else:
            self.buttonLeft = tk.Canvas(self.frame, **config['Left']['Canvas'])
        self.buttonLeft.place(**config['Left']['place'])
        if 'Right' in self.elements.keys():
            self.buttonRight = tk.Button(self.frame, font = self.font())
            self.buttonRight.config(**config['Right']['Button'])
            self.buttonRight.configure(command=self.Right)
        else:
            self.buttonRight = tk.Canvas(self.frame, **config['Right']['Canvas'])
        self.buttonRight.place(**config['Right']['place'])
        if 'Center' in self.elements.keys():
            self.buttonCenter = tk.Button(self.frame, font = self.font())
            self.buttonCenter.config(text=self.settings['Label'])
            self.buttonCenter.configure(command=self.Center)
        else:
            self.buttonCenter = tk.Canvas(self.frame, **config['Center']['Canvas'])
        self.buttonCenter.place(**config['Center']['place'])
        self.frame.config(**config['frame'])
        self.frame.pack()

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
        config = self.root.settings['widget']['pistonbutton']
        if 'Left' in self.elements.keys():
            bd = 1
            color = []
            if 'coil' in self.elements['Left']:
                if self.elements['Left']['coil']:
                    color.append('coil')
            if 'sensor' in self.elements['Left']:
                if self.elements['Left']['sensor']: 
                    color.append('sensor')
                    bd = 4
            if 'coil' in color and 'sensor' in color:
                color = config['Color']['empowered']
            elif 'coil' in color:
                color = config['Color']['active']
            elif 'sensor' in color:
                color = config['Color']['highlighted']
            else:
                color = config['Color']['normal']
            self.buttonLeft.configure(background = color, borderwidth = bd)
        if 'Right' in self.elements.keys():
            color = []
            bd = 1
            if 'coil' in self.elements['Right']:
                if self.elements['Left']['coil']:
                    color.append('coil')
            if 'sensor' in self.elements['Right']:
                if self.elements['Left']['sensor']: 
                    color.append('sensor')
                    bd = 4
            if 'coil' in color and 'sensor' in color:
                color = config['Color']['empowered']
            elif 'coil' in color:
                color = config['Color']['active']
            elif 'sensor' in color:
                color = config['Color']['highlighted']
            else:
                color = config['Color']['normal']
            self.buttonRight.configure(background = color, borderwidth = bd)
        if 'Center' in self.elements.keys():
            color = []
            bd = 1
            if 'coil' in self.elements['Center']:
                if self.elements['Center']['coil']:
                    color.append('coil')
            if 'sensor' in self.elements['Center']:
                if self.elements['Center']['sensor']: 
                    color.append('sensor')
                    bd = 4
            if 'coil' in color and 'sensor' in color:
                color = config['Color']['empowered']
            elif 'coil' in color:
                color = config['Color']['active']
            elif 'sensor' in color:
                color = config['Color']['highlighted']
            else:
                color = config['Color']['normal']
            self.buttonCenter.configure(background = color, borderwidth = bd)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)