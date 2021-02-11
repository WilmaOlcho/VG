import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json

def getroot(obj):
    while True:
        if hasattr(obj,'master'):
            if obj.master:
                obj = obj.master
            else:
                break
        else:
            break
    return obj

class HomeScreen(dict):
    def __init__(self, master = None):
        super().__init__()
        self['settings'] = master.settings['HomeScreen']
        self.frame = ttk.Frame(master = master)
        self.frame.__setattr__('settings',self['settings'])
        self.root = getroot(master)
        self.name = self['settings']['Name']
        self.font = self.root.font
        self.widgets = [
            FirstColumn(self),
            SecondColumn(self),
            ThirdColumn(self)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.LEFT, expand = tk.Y)
        self.pack(expand = tk.YES, fill=tk.BOTH)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class ThirdColumn(dict):
    def __init__(self, master = None):
        super().__init__()
        self['settings'] = master.settings['ThirdColumn']
        self.frame = tk.Frame(master = master)
        self.frame.__setattr__('settings',self['settings'])
        self.root = getroot(master)
        self.font = self.root.font
        self.widgets = [
            ProcessVariables(self)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class ProcessVariables(dict):
    def __init__(self, master = None):
        super().__init__()
        self.root = getroot(master)
        self['settings'] = master.settings['ProcessVariables']
        self.frame = ttk.LabelFrame(master = master, text = self['settings']['Label'])
        self.frame.__setattr__('settings',self['settings'])
        self.font = master.font
        self.leftFrame = ttk.Frame(self.frame)
        self.rightFrame = ttk.Frame(self.frame)
        self.widgets = [
            variablesFrame(master = self.leftFrame, key = 'currentposition'),
            variablesFrame(master = self.leftFrame, key = 'processtime'),
            tk.Button(master = self.rightFrame, font = self.font(), command = self.stepclick, **self['settings']['button']['step']),
            tk.Button(master = self.rightFrame, font = self.font(), command = self.startclick, **self['settings']['button']['start']),
            tk.Button(master = self.rightFrame, font = self.font(), command = self.stopclick, **self['settings']['button']['stop']),
            self.leftFrame,
            self.rightFrame
        ]
        for widget in self.widgets:
            widget.pack(side = tk.LEFT if widget.master == self else tk.TOP, fill ='x', anchor = tk.S)
        self.frame.pack()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def stepclick(self):
        if not self.root.variables['ProgramActive']:
            self.root.variables['auto'] = not self.root.variables['auto']

    def startclick(self):
        self.root.variables['ProgramActive'] = True
        self.root.variables.internalEvents['start'] = True

    def stopclick(self):
        self.root.variables['ProgramActive'] = False
        self.root.variables.internalEvents['stop'] = True

    def update(self):
        super().update()
        for widget in self.widgets:
            if isinstance(widget, tk.Button):
                button = widget.cget('text')
                if button == 'Praca krokowa':
                    if self.root.variables['auto']:
                        widget.configure(text = 'Praca automatyczna')
                elif button == 'Praca automatyczna':
                    if not self.root.variables['auto']:
                        widget.configure(text = 'Praca krokowa')
                elif button == 'Uruchom':
                    widget.configure(bg = 'lightgreen' if self.root.variables['ProgramActive'] else 'green')
                elif button == 'Zatrzymaj':
                    widget.configure(bg = 'red' if self.root.variables['ProgramActive'] else 'red')
            widget.update()

class variablesFrame(dict):
    def __init__(self, master = None, key = 'auto'):
        super().__init__()
        self.frame = tk.Frame(master = master)
        self.key = key
        self['settings'] = master.settings[key]
        self.frame.__setattr__('settings',self['settings'])
        self.root = getroot(master)
        self.font = self.root.font
        self.widgets = [
            ttk.Label(master = self.frame, text = self['settings']['Label']),
            ttk.Entry(master = self, text =self.root.variables[self.key], width = self['settings']['width'])
        ]
        for widget in self.widgets:
            widget.pack()
        self.pack()

    def update(self):
        super().update()
        for widget in self.widgets:
            if isinstance(widget,tk.Entry):
                widget.delete(0,tk.END)
                widget.insert(0,self.root.variables[self.key])
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class SecondColumn(ttk.Frame):
    def __init__(self, master = None):
        super().__init__(master = master)
        self.root.variables = variables
        self.master = master
        self.widgets = [
            StatusIndicators(self, variables = self.root.variables)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class FirstColumn(ttk.Frame):
    def __init__(self, master = None):
        super().__init__(master = master)
        self.root.variables = variables
        self.master = master
        self.widgets = [
            ProgramSelect(self, variables = self.root.variables),
            Positions(self, variables = self.root.variables)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()
    
    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class StatusIndicators(ttk.LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, text = 'Status')
        self.root.variables = variables
        self.widgets = [
            StatusIndicators.line(self, variables = self.root.variables, label = 'Bezpieczeństwo:', indicator = 'Safety'),
            StatusIndicators.line(self, variables = self.root.variables, label = 'Gaz osłonowy:', indicator = 'ShieldingGas'),
            StatusIndicators.line(self, variables = self.root.variables, label = 'Filtrowentylator:', indicator = 'VacuumFilter'),
            StatusIndicators.line(self, variables = self.root.variables, label = 'Powietrze:', indicator = 'Air'),
            StatusIndicators.line(self, variables = self.root.variables, label = 'Krosdżet:', indicator = 'Crossjet'),
            StatusIndicators.line(self, variables = self.root.variables, label = 'Wózek', indicator = 'Troley'),
            StatusIndicators.line(self, variables = self.root.variables, label = 'Oświetlenie:', indicator = 'Light'),
            StatusIndicators.line(self, variables = self.root.variables, label = 'Robot', indicator = 'Robot')
        ]
        for widget in self.widgets:
            widget.pack()
        self.pack()
    
    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()
        
    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    class line(ttk.Frame):
        def __init__(self, master = None, variables = Variables(), label = '', indicator = ''):
            super().__init__(master = master, height='30', width='135', borderwidth = 2, relief = 'ridge')
            self.key = indicator
            self.root.variables = variables
            self.label = ttk.Label(self)
            self.label.config(text=label)
            self.label.place(anchor='w', x='3', y='13')
            self.indicator = tk.Canvas(self)
            self.indicator.config(background='Black', height='22', width='22', bd = 0)
            self.indicator.place(anchor='e', x='130', y='14')
            self.pack()
        
        def update(self):
            super().update()
            self.indicator.config(bg = 'lightgreen' if self.root.variables.statusindicators[self.key]==1 else 'black' if self.root.variables.statusindicators[self.key]==0 else 'red')

class ProgramSelect(ttk.LabelFrame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master, text = 'Program')
        self.menubutton = tk.Menubutton(master = self, text = 'Program')
        self.root.variables = variables
        self.root.variables.jsonpath = str(Path(__file__).parent.absolute())+'\\Programs.json'
        self.programs = json.load(open(self.root.variables.jsonpath))
        self.menu = tk.Menu(master = self.menubutton, tearoff = 0)
        self.menubutton['menu'] = self.menu
        for program in self.programs["Programs"]:
            self.menu.add_command(label = program['Name'], command = lambda obj = self, program = program['Name']: obj.command(program))
        self.menubutton.pack()

    def command(self, program):
        self.menubutton.config(text = program)
        self.root.variables.currentProgram = program
        for prog in self.programs['Programs']:
            if prog['Name'] == program:
                self.root.variables.programposstart = min(int(item[1]) for item in prog['Table'])
                self.root.variables.programposend = max(int(item[1]) for item in prog['Table'])
                break
        self.root.variables.internalEvents['RefreshStartEnd'] = True
        self.root.variables.internalEvents['TableRefresh'] = True

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class Positions(ttk.LabelFrame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master, text = 'Wybór pozycji')
        self.root.variables = variables
        self.programs = json.load(open(self.root.variables.jsonpath))
        self.program = {}
        self.widgets = [
            ttk.Label(master = self, text = 'OD '),
            ttk.Entry(master = self, text = ''),
            ttk.Label(master = self, text = 'DO '),
            ttk.Entry(master = self, text = '')
        ]
        for widget in self.widgets:
            if isinstance(widget, tk.Entry):
                widget.config(width = 5)
                widget.bind("<FocusOut>",lambda x, obj = self: obj.setvalue())
            widget.pack(side = tk.LEFT, anchor = tk.N)
        self.pack()
        
    def nearest(self, value, attempts = list()):
        attemptlist = attempts.copy()
        attemptlist.sort(key = lambda element, v = int(value): abs(v - int(element)))
        return attemptlist[0]

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def setvalue(self):
        for widget in self.widgets:
            if isinstance(widget, tk.Entry):
                value = widget.get()
                if not value.isnumeric(): break
                value = int(value)
                positionsintable = [item[1] for item in self.program['Table']]
                if not value in positionsintable:
                    value = self.nearest(value, positionsintable)
                if '2' in widget._name:
                    self.root.variables.programposend = value
                else:
                    self.root.variables.programposstart = value
        self.root.variables.internalEvents['RefreshStartEnd'] = True
        
    def update(self):
        super().update()
        for program in self.programs['Programs']:
            if program['Name'] == self.root.variables.currentProgram:
                self.program = program
        if self.root.variables.internalEvents['RefreshStartEnd']:
            for widget in self.widgets:
                if 'entry' in widget._name:
                    widget.delete(0,tk.END)
                    if '2' in widget._name:
                        widget.insert(0,str(self.root.variables.programposend))
                    else:
                        widget.insert(0,str(self.root.variables.programposstart))
        self.root.variables.internalEvents['RefreshStartEnd'] = False

        
