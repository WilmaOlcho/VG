import tkinter as tk
from tkinter import ttk
from .Variables import Variables
from .Widgets.callableFont import Font
from .Widgets import GeneralWidget, LabelFrame, Button, Entry, Lamp

class SettingsScreen(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'SettingsScreen')
        self.name = self.settings['Name']
        self.miscpneumaticsframe = LabelFrame(master = self.frame, branch = "Pneumatics")
        self.miscpneumaticsframe.__setattr__('settings', self.settings['Pneumatics'])
        self.widgets = [
            Troley(self.frame),
            Laser(self.frame),
            Robot(self.frame),
            PistonControl(master = self.miscpneumaticsframe.frame, button = 'ShieldingGas'),
            PistonControl(master = self.miscpneumaticsframe.frame, button = 'CrossJet'),
            PistonControl(master = self.miscpneumaticsframe.frame, button = 'HeadCooling'),
            self.miscpneumaticsframe
        ]
        self.buttonsframe = tk.Frame(master = self.frame)
        for number, widget in enumerate(self.widgets):
            if isinstance(widget, LabelFrame):
                button = tk.Button(master = self.buttonsframe, font = self.font(), text = widget.settings['Label'], command = lambda obj = self, key = number: obj.show(key), **self.settings['Button'])
                button.pack(side = tk.TOP, anchor = tk.NW)
            else:
                widget.pack(anchor = tk.NW)
        self.buttonsframe.pack(side = tk.LEFT, anchor = tk.NW)
        self.pack(expand = tk.YES, fill=tk.BOTH)

    def show(self, key):
        for number, widget in enumerate(self.widgets):
            if number == key:
                widget.pack(side = tk.LEFT, anchor = tk.NW)
            else:
                if isinstance(widget, LabelFrame):
                    widget.pack_forget()

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

class Robot(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'Robot')
        self.buttonsframe = tk.Frame(self.frame)
        self.buttonsframe.__setattr__('settings', self.settings)
        self.lampsframe = tk.Frame(self.frame)
        self.lampsframe.__setattr__('settings', self.settings)
        self.entriesframe = tk.Frame(self.frame)
        self.entriesframe.__setattr__('settings', self.settings)
        self.widgets = [self.buttonsframe, self.lampsframe, self.entriesframe]
        buttons = self.settings['buttons']
        lamps = self.settings['lamps']
        entries = self.settings['entries']
        for key, value in buttons.items():
            self.widgets.append(Button(self.buttonsframe, text = key, key = value))
        for key, value in lamps.items():
            self.widgets.append(Lamp(self.lampsframe, text = key, key = value))
        for key, value in entries.items():
            self.widgets.append(Entry(self.entriesframe, text = key, key = value))
        for widget in self.widgets:
            if widget.master == self.frame:
                widget.pack(side = tk.LEFT, anchor = tk.N)
            else:
                widget.pack(anchor = tk.N)

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
