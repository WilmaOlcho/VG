import tkinter as tk
from tkinter import ttk
from Variables import Variables
from Widgets.callableFont import Font
from getroot import getroot

class GeneralWidget(dict):
    def __init__(self, master = None, branch = ''):
        super().__init__()
        self.settings = master.settings[branch] if branch else master.settings
        self.frame = ttk.Frame(master = master)
        self.frame.__setattr__('settings', self.settings)
        self.root = getroot(master)
        self.widgets = []
        self.font = self.root.font
        self.master = master

    def update(self):
        self.frame.update()
        for widget in self.widgets:
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class LabelFrame(GeneralWidget):
    def __init__(self, master = None, branch = ''):
        super().__init__(master = master, branch = branch)
        self.frame = ttk.LabelFrame(master = master, text = self.settings['Label'])
        self.frame.__setattr__('settings', self.settings)

class SettingsScreen(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'SettingsScreen')
        self.name = self.settings['Name']
        self.miscpneumaticsframe = ttk.LabelFrame(master = self.frame, text = self.settings["Pneumatics"]['Label'])
        self.miscpneumaticsframe.__setattr__('settings', self.settings['Pneumatics'])
        self.widgets = [
            Troley(self.frame),
            Laser(self.frame),
            PistonControl(master = self.miscpneumaticsframe, button = 'ShieldingGas'),
            PistonControl(master = self.miscpneumaticsframe, button = 'CrossJet'),
            PistonControl(master = self.miscpneumaticsframe, button = 'HeadCooling'),
            self.miscpneumaticsframe
        ]
        for widget in self.widgets:
            if isinstance(widget, LabelFrame):
                widget.pack(side = tk.LEFT, anchor = tk.NW)
            else:
                widget.pack(anchor = tk.NW)
        self.frame.pack(expand = tk.YES, fill=tk.BOTH)

class Troley(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'Troley')
        self.pistonlabeledFrame = ttk.LabelFrame(self.frame, text = self.settings['Pneumatics']['Label'])
        self.pistonlabeledFrame.__setattr__('settings', self.settings['Pneumatics'])
        self.widgets.append(ServoControl(master = self.frame))
        self.widgets.append(self.pistonlabeledFrame)
        for piston in self.settings['Pneumatics']:
            if piston == 'Label': continue
            self.widgets.append(PistonControl(master = self.pistonlabeledFrame, button=piston))
        for widget in self.widgets:
            widget.pack(anchor = tk.NW)
        self.pack()

class Laser(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'Laser')
        self.buttonsframe = tk.Frame(self.frame)
        self.buttonsframe.__setattr__('settings', self.settings)
        self.lampsframe = tk.Frame(self.frame)
        self.lampsframe.__setattr__('settings', self.settings)
        self.widgets = [self.buttonsframe, self.lampsframe]
        buttons = self.settings['buttons']
        lamps = self.settings['lamps']
        for key, value in buttons.items():
            self.widgets.append(Button(self.buttonsframe, text = key, key = value))
        for key, value in lamps.items():
            self.widgets.append(Lamp(self.lampsframe, text = key, key = value))
        for widget in self.widgets:
            if widget.master == self.frame:
                widget.pack(side = tk.LEFT, anchor = tk.N)
            else:
                widget.pack(anchor = tk.N)
        self.pack()

class ServoControl(LabelFrame):
    def __init__(self, master = None, buttons = {}, lamps = {}):
        super().__init__(master = master, branch = 'Servo')
        self.buttonsframe = tk.Frame(self.frame)
        self.buttonsframe.__setattr__('settings', self.settings)
        self.lampsframe = tk.Frame(self.frame)
        self.lampsframe.__setattr__('settings', self.settings)
        self.widgets = [self.buttonsframe, self.lampsframe]
        buttons = self.settings['buttons']
        lamps = self.settings['lamps']
        for key, value in buttons.items():
            self.widgets.append(Button(self.buttonsframe, text = key, key = value))
        for key, value in lamps.items():
            self.widgets.append(Lamp(self.lampsframe, text = key, key = value))
        for widget in self.widgets:
            if widget.master == self.frame:
                widget.pack(side = tk.LEFT, anchor = tk.N)
            else:
                widget.pack(anchor = tk.N)
        self.pack()

class Button(GeneralWidget):
    def __init__(self, master = None, text = '', key = ''):
        super().__init__(master = master, branch = 'Button')
        self.frame = tk.Button(master = master, font = self.font(), text = text, command = self.click, width = self.settings['width'], height = self.settings['height'])
        self.frame.__setattr__('settings',self.settings)
        self.key = key
        self.masterkey = self.settings['masterkey']

    def click(self):
        if self.key[0] == '-':
            self.root.variables[self.masterkey][self.key[1:]] = False
        else:
            self.root.variables[self.masterkey][self.key] = True

class Lamp(GeneralWidget):
    def __init__(self, master = None, text = '', key = ''):
        super().__init__(master = master, branch = 'Lamp')
        self.frame = tk.Frame(master, **self.settings['frame'])
        self.frame.__setattr__('settings',self.settings)
        self.lamp = tk.Canvas(master = self.frame, width = self.settings['width'], height = self.settings['height'])
        self.caption = ttk.Label(master = self.frame, text = text, **self.settings['caption'])
        self.key = key
        self.masterkey = self.settings['masterkey']
        self.caption.pack(side = tk.LEFT)
        self.lamp.pack(side = tk.LEFT)
        self.lit = False

    def update(self):
        self.frame.update()
        negation = '-' in self.key[:2]
        errsign = '!' in self.key[:2]
        keystartpos = 0 + 1 if negation else 0 + 1 if errsign else 0
        key = self.key[keystartpos:]
        if negation:
            self.lit = not self.root.variables[self.masterkey][key]
        else:
            self.lit = self.root.variables[self.masterkey][key]
        if errsign:
            self.lamp.config(bg = self.settings['Color']['error'] if self.lit else self.settings['Color']['normal'])
        else:
            self.lamp.config(bg = self.settings['Color']['active'] if self.lit else self.settings['Color']['normal'])

class PistonControl(GeneralWidget):
    def __init__(self, master = None, button = "", **kwargs):
        super().__init__(master = master, branch = button)
        config = self.root.settings['widget']['pistonbutton']
        self.frame = tk.Frame(master = master, **config['frame'])
        self.frame.__setattr__('settings',self.settings)
        self.elements = self.root.variables[self.settings['masterkey']][self.settings['key']]
        if 'Left' in self.elements.keys():
            self.buttonLeft = tk.Button(self.frame, font = self.font(), **config['Left']['Button'])
            self.buttonLeft.configure(command=self.Left)
        else:
            self.buttonLeft = tk.Canvas(self.frame, **config['Left']['Canvas'])
        self.buttonLeft.place(**config['Left']['place'])
        if 'Right' in self.elements.keys():
            self.buttonRight = tk.Button(self.frame, font = self.font(), **config['Right']['Button'])
            self.buttonRight.configure(command=self.Right)
        else:
            self.buttonRight = tk.Canvas(self.frame, **config['Right']['Canvas'])
        self.buttonRight.place(**config['Right']['place'])
        if 'Center' in self.elements.keys():
            self.buttonCenter = tk.Button(self.frame, font = self.font(), **config['Center']['Button'])
            self.buttonCenter.config(text=self.settings['Label'])
            self.buttonCenter.configure(command=self.Center)
        else:
            self.buttonCenter = tk.Canvas(self.frame, **config['Center']['Canvas'])
        self.buttonCenter.place(**config['Center']['place'])
        self.pack()

    def Left(self):
        self.elements['Left']['coil'] = not self.elements['Left']['coil']
        if 'Right' in self.elements:
            if 'coil' in self.elements['Right']: 
               self.elements['Right']['coil'] = False

    def Right(self):
        self.elements['Right']['coil'] = not self.elements['Right']['coil']
        if 'Left' in self.elements:
            if 'coil' in self.elements['Left']: 
                self.elements['Left']['coil'] = False
        
    def Center(self):
        if 'Right' in self.elements:
            self.elements['Right']['coil'] = False
        if 'Left' in self.elements:
            self.elements['Left']['coil'] = False
        
    def update(self):
        self.frame.update()
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
                if self.elements['Right']['coil']:
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
