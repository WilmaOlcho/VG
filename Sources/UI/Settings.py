import tkinter as tk
from tkinter import ttk
from .Variables import Variables
from .Widgets.callableFont import Font
from .Widgets import GeneralWidget, LabelFrame, Button 
from .Widgets import Entry, Lamp, Frame, KEYWORDS
from .Widgets import StatusIndicators, VariablesFrames
from .Widgets import Window

class SettingsScreen(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'SettingsScreen')
        self.name = self.settings['Name']
        self.miscpneumaticsframe = LabelFrame(master = self, branch = "Pneumatics")
        self.widgets = [
            Troley(self),
            Laser(self),
            Robot(self),
            Scout(self),
            Safety(self),
            PistonControl(master = self.miscpneumaticsframe, button = 'ShieldingGas'),
            PistonControl(master = self.miscpneumaticsframe, button = 'CrossJet'),
            PistonControl(master = self.miscpneumaticsframe, button = 'HeadCooling'),
            self.miscpneumaticsframe
        ]
        self.buttons = []
        self.buttonsframe = tk.Frame(master = self)
        for number, widget in enumerate(self.widgets):
            if isinstance(widget, LabelFrame):
                self.buttons.append(tk.Button(master = self.buttonsframe, font = self.font(), text = widget.settings['Label'], command = lambda obj = self, key = number: obj.show(key), **self.settings['Button']))
                self.buttons[number].pack(side = tk.TOP, anchor = tk.NW)
            else:
                self.buttons.append(None)
                widget.pack(anchor = tk.NW)
        self.buttonsframe.pack(side = tk.LEFT, anchor = tk.NW)
        self.pack(expand = tk.YES, fill=tk.BOTH)

    def show(self, key):
        for number, widget in enumerate(self.widgets):
            if number == key:
                widget.pack(side = tk.LEFT, anchor = tk.NW)
                if isinstance(self.buttons[number], tk.Button):
                    self.buttons[number].config(relief='sunken')
            else:
                if isinstance(self.buttons[number], tk.Button):
                    self.buttons[number].config(relief='ridge')
                if isinstance(widget, LabelFrame):
                    widget.pack_forget()

class Troley(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'Troley')
        self.pistonlabeledFrame = LabelFrame(self, branch = 'Pneumatics')
        self.buttonsframe = Frame(self)
        ServoControl(master = self)
        for piston in self.settings['Pneumatics']:
            if piston in KEYWORDS: continue
            PistonControl(master = self.pistonlabeledFrame, button=piston).pack(anchor = tk.N)
        for key, value in self.settings['buttons'].items():
            Button(self.buttonsframe, text = key, key = value).pack(anchor = tk.N)
        for widget in self.winfo_children():
            widget.pack(anchor = tk.NW)

class Laser(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'Laser')
        self.buttonsframe = Frame(self)
        StatusIndicators(self)
        for key, value in self.settings['buttons'].items():
            Button(self.buttonsframe, text = key, key = value).pack(anchor = tk.N)
        for widget in self.winfo_children():
            widget.pack(side = tk.LEFT, anchor = tk.N)

class Safety(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'Safety')
        self.buttonsframe = Frame(self)
        StatusIndicators(self)
        for key, value in self.settings['buttons'].items():
            Button(self.buttonsframe, text = key, key = value).pack(anchor = tk.N)
        for widget in self.winfo_children():
            widget.pack(side = tk.LEFT, anchor = tk.N)

class Scout(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'Scout')
        self.buttonsframe = Frame(self)
        StatusIndicators(self)
        VariablesFrames(self)
        self.versionlabel = tk.Label(self)
        for key, value in self.settings['buttons'].items():
            Button(self.buttonsframe, text = key, key = value).pack(anchor = tk.N)
        for widget in self.winfo_children():
            widget.pack(side = tk.LEFT, anchor = tk.N)

    def update(self):
        super().update()
        if self.root.variables['scout']['showaligninfo']:
            window = AlignInfoWindow(self)
            window.grab_set()
            self.root.variables['scout']['showaligninfo'] = False

class AlignInfoWindow(Window):
    def __init__(self, master = None, cls = None, args = ()):
        super().__init__(master, branch = "")
        ttk.Label(self, text = "Różnica trajektorii").grid(column = 0, columnspan = 2, row = 0)
        ttk.Label(self, text = 'Kąt').grid(column = 0, row = 1)
        self.A = tk.Entry(self, width = 15)
        self.A.grid(column = 1, row = 1)
        ttk.Label(self, text = 'X').grid(column = 0, row = 2)
        self.X = tk.Entry(self, width = 15)
        self.X.grid(column = 1, row = 2)
        ttk.Label(self, text = 'Y').grid(column = 0, row = 3)
        self.Y = tk.Entry(self, width = 15)
        self.Y.grid(column = 1, row = 3)
        self.center()
        Button(master = self, text = "Ok", callback = self.destroy).grid(column = 0, row = 4, columnspan = 2)

    def update(self):
        if not self.destroyed:
            super().update()
            A = self.A.get()
            X = self.X.get()
            Y = self.Y.get()
            if float(A if A else 'inf') != self.root.variables['scout']['AlignInfoA']:
                self.A.delete(0,tk.END)
                self.A.insert(0,self.root.variables['scout']['AlignInfoA'])
            if float(X if X else 'inf') != self.root.variables['scout']['AlignInfoX']:
                self.X.delete(0,tk.END)
                self.X.insert(0,self.root.variables['scout']['AlignInfoX'])
            if float(Y if Y else 'inf') != self.root.variables['scout']['AlignInfoY']:
                self.Y.delete(0,tk.END)
                self.Y.insert(0,self.root.variables['scout']['AlignInfoY'])

class Robot(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'Robot')
        self.buttonsframe = Frame(self)
        StatusIndicators(self)
        self.entriesframe = Frame(self)
        for key, value in self.settings['buttons'].items():
            Button(self.buttonsframe, text = key, key = value).pack(anchor = tk.N)
        for key, value in self.settings['entries'].items():
            Entry(self.entriesframe, text = key, key = value).pack(anchor = tk.N)
        for widget in self.winfo_children():
            widget.pack(side = tk.LEFT, anchor = tk.N)

class ServoControl(LabelFrame):
    def __init__(self, master = None, buttons = {}, lamps = {}):
        super().__init__(master = master, branch = 'Servo')
        self.buttonsframe = Frame(self)
        statusframe = StatusIndicators(self)
        for key, value in self.settings['buttons'].items():
            Button(self.buttonsframe, text = key, key = value).pack(anchor = tk.N)
        Entry(statusframe)
        for widget in self.winfo_children():
            widget.pack(side = tk.LEFT, anchor = tk.N)

class PistonControl(GeneralWidget):
    def __init__(self, master = None, button = "", **kwargs):
        super().__init__(master = master, branch = button)
        config = self.root.settings['widget']['pistonbutton']
        self.config(**config['frame'])
        self.elements = self.root.variables[self.settings['masterkey']][self.settings['key']]
        if 'Left' in self.elements.keys():
            self.buttonLeft = tk.Button(self, font = self.font(), **config['Left']['Button'])
            self.buttonLeft.configure(command=self.Left)
        else:
            self.buttonLeft = tk.Canvas(self, **config['Left']['Canvas'])
        self.buttonLeft.place(**config['Left']['place'])
        if 'Right' in self.elements.keys():
            self.buttonRight = tk.Button(self, font = self.font(), **config['Right']['Button'])
            self.buttonRight.configure(command=self.Right)
        else:
            self.buttonRight = tk.Canvas(self, **config['Right']['Canvas'])
        self.buttonRight.place(**config['Right']['place'])
        if 'Center' in self.elements.keys():
            self.buttonCenter = tk.Button(self, font = self.font(), **config['Center']['Button'])
            self.buttonCenter.config(text=self.settings['Label'])
            self.buttonCenter.configure(command=self.Center)
        else:
            self.buttonCenter = tk.Canvas(self, **config['Center']['Canvas'])
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
        super().update()
