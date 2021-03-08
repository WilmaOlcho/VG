import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json
from getroot import getroot
from win32api import GetSystemMetrics

class HomeScreen(dict):
    def __init__(self, master = None):
        super().__init__()
        self.frame = ttk.Frame(master = master)
        self.settings = master.settings['HomeScreen']
        self.frame.__setattr__('settings',self.settings)
        self.root = getroot(master)
        self.frame.__setattr__('settings', self.settings)
        self.name = self.settings['Name']
        self.font = self.root.font
        self.widgets = []
        for key in self.settings.keys():
            if not key == 'Name':
                self.widgets.append(eval(key)(self.frame))
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
        self.root = getroot(master)
        self.settings = master.settings['ThirdColumn']
        self.frame = tk.Frame(master = master)
        self.frame.__setattr__('settings', self.settings)
        self.font = self.root.font
        self.widgets = []
        for key in self.settings:
            self.widgets.append(eval(key)(master = self.frame))
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

    def update(self):
        self.frame.update()
        for widget in self.widgets:
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class ProcessVariables(dict):
    def __init__(self, master = None):
        super().__init__()
        self.root = getroot(master)
        self.settings = master.settings['ProcessVariables']
        self.frame = ttk.LabelFrame(master = master, text = self.settings['Label'])
        self.frame.__setattr__('settings',self.settings)
        self.font = self.root.font
        self.leftFrame = ttk.Frame(master = self.frame)
        self.leftFrame.__setattr__('settings',self.settings)
        self.rightFrame = ttk.Frame(master = self.frame)
        self.rightFrame.__setattr__('settings',self.settings)
        self.widgets = [
            self.leftFrame,
            self.rightFrame
        ]
        for key in self.settings['variablesFrame'].keys():
            self.widgets.append(variablesFrame(master = self.leftFrame, key = key))
        for key in self.settings['Button'].keys():
            button = tk.Button(master = self.rightFrame, font = self.font(), command = lambda obj = self, k = key: obj.click(k), **self.settings['Button'][key])
            button.__setattr__('settings',self.settings['interactive'][key])
            self.widgets.append(button)
        for widget in self.widgets:
            widget.pack(side = tk.LEFT if isinstance(widget, ttk.Frame) else tk.TOP, fill ='x', anchor = tk.N)
        self.pack()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def click(self, key):
        for widget in self.widgets:
            if 'action' in widget.settings:
                action = widget.settings['action']
                anticondition = eval(widget.settings['anticondition']) if 'anticondition' in widget.settings else False
                if action == key and not anticondition:
                    result = widget.settings['result'].split('\n')
                    for line in result:
                        if '=' in line:
                            exec(line)
                        else:
                            eval(line)

    def update(self):
        self.frame.update()
        for widget in self.widgets:
            if isinstance(widget, tk.Button):
                if 'condition' in widget.settings.keys():
                    condition = eval(widget.settings['condition'])
                    if condition:
                        widget.config(widget.settings['active'])
                    else:
                        widget.config(widget.settings['inactive'])

class variablesFrame(dict):
    def __init__(self, master = None, key = 'auto'):
        super().__init__()
        self.frame = tk.Frame(master = master)
        self.key = key
        self.settings = master.settings['variablesFrame'][key]
        self.frame.__setattr__('settings',self.settings)
        self.root = getroot(master)
        self.font = self.root.font
        self.widgets = [
            ttk.Label(master = self.frame, text = self.settings['Label']),
            ttk.Entry(master = self.frame, text = self.root.variables[self.key], width = self.settings['width'])
        ]
        for widget in self.widgets:
            widget.pack(side = tk.TOP)
        self.pack()

    def update(self):
        self.frame.update()
        for widget in self.widgets:
            if isinstance(widget,tk.Entry):
                widget.delete(0,tk.END)
                widget.insert(0,self.root.variables[self.key])
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class SecondColumn(dict):
    def __init__(self, master = None):
        super().__init__()
        self.root = getroot(master)
        self.frame = ttk.Frame(master = master)
        self.settings = master.settings['SecondColumn']
        self.frame.__setattr__('settings', self.settings)
        self.widgets = [
            StatusIndicators(master = self.frame)
        ]
        for widget in self.widgets:
            widget.frame.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

    def update(self):
        self.frame.update()
        for widget in self.widgets:
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class FirstColumn(dict):
    def __init__(self, master = None):
        super().__init__()
        self.frame = ttk.Frame(master = master)
        self.root = getroot(master)
        self.settings = master.settings['FirstColumn']
        self.frame.__setattr__('settings', self.settings)
        self.widgets = [
            ProgramSelect(self.frame),
            Positions(self.frame)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

    def update(self):
        self.frame.update()
        for widget in self.widgets:
            widget.update()
    
    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class NewProgramWindow(tk.Toplevel):
    def __init__(self, parent, menubuttonwidget):
        super().__init__(parent)
        self.title('Nowy program')
        self.master = parent
        self.masterwidget = menubuttonwidget
        self.frame = ttk.LabelFrame(master = self, text = 'Program bazowy')
        self.menubutton = tk.Menubutton(master = self.frame, height = 3, width = 70, text = 'Wybierz program bazowy', bg = 'white')
        self.menu = tk.Menu(master = self.menubutton)
        self.menubutton['menu'] = self.menu
        self.root = getroot(parent)
        with open(self.root.variables.jsonpath) as jsonfile:
            self.programs = json.load(jsonfile)
        self.menu.add_command(label = 'Pusty', command = self.command)
        for program in self.programs["Programs"]:
            self.menu.add_command(label = program['Name'], command = lambda obj = self, program = program['Name']: obj.command(program))
        self.menubutton.pack()
        self.frame.grid(column = 0, row = 0, columnspan = 3)
        self.nameentry = tk.Entry(master = self, text = "Nazwa nowego programu")
        self.nameentry.bind('<FocusIn>', self.nameentryclicked)
        self.nameentry.bind('<FocusOut>', self.nameentryreleased)
        self.NameentryLabel = ttk.Label(master = self, text = "Nazwa dla nowego programu")
        self.NameentryLabel.grid(column = 0, row = 1)
        self.nameentry.grid(column = 1, columnspan = 2, row= 1)
        self.buttonDoIt = ttk.Button(master = self, text = 'Utwórz program', command = self._newprogram)
        self.buttonCancel = ttk.Button(master = self, text = 'Zaniechaj', command = self.cancel)
        self.buttonDoIt.grid(column = 0, row = 2, sticky = tk.W)
        self.buttonCancel.grid(column = 2, row = 2, sticky = tk.E)
        self.newprogram = {}
        self.name = ''
        self.center()

    def center(self):
        screenWidth = GetSystemMetrics(0)
        screenHeigth = GetSystemMetrics(1)
        size = tuple(int(val) for val in self.geometry().split('+')[0].split('x'))
        x = int(screenWidth/2 - size[0]/2)
        y = int(screenHeigth/2 - size[1]/2)
        self.geometry('+{}+{}'.format(x,y))

    def nameentryreleased(self, event):
        self.name = self.nameentry.get()
        self.nameentry.config(bg = 'white')

    def nameentryclicked(self, event):
        self.nameentry.config(bg = 'lightblue')

    def command(self, program = 'Pusty'):
        if program == 'Pusty' or program == "empty":
            self.newprogram = {
                "Name":"New",
                "Table":[[0, 0, "", 0, 0, 0, 0, 0, 0]]
            }
        else:
            for _program in self.programs["Programs"]:
                if _program['Name'] == program:
                    self.newprogram = _program.copy()
                    self.newprogram['Name'] = 'New'
                    break
        self.menubutton.config(text = program)
        self.root.variables.currentProgram = program

    def _newprogram(self):
        if self.newprogram:
            self.getnameforprogram()
            self.newprogram['Name'] = self.name
            self.masterwidget.config(text = self.name)
            self.programs['Programs'].append(self.newprogram)
            with open(self.root.variables.jsonpath, 'w') as jsonfile:
                json.dump(self.programs, jsonfile)
            self.root.variables.currentProgram = self.name
            self.root.variables.internalEvents['TableRefresh'] = True
            self.root.variables.internalEvents['RefreshStartEnd'] = True
            self.root.variables.internalEvents['ProgramMenuRefresh'] = True
        self.destroy()

    def cancel(self):
        self.destroy()

    def getnameforprogram(self):
        self.name = self.nameentry.get()
        if not self.name: self.name = "New"
        iteration = 0
        changed = True
        while changed:
            changed = False
            for _program in self.programs['Programs']:
                nametocheck = self.name + (str(iteration) if iteration else '')
                if _program['Name'] == nametocheck:
                    iteration +=1
                    changed = True
                    break
        self.name += str(iteration) if iteration else ''
        pass

class DeleteProgramWindow(tk.Toplevel):
    def __init__(self, parent, menubuttonwidget):
        super().__init__(parent)
        self.title('Usuń program')
        self.master = parent
        self.masterwidget = menubuttonwidget
        self.frame = ttk.LabelFrame(master = self, text = 'Program do usunięcia')
        self.menubutton = tk.Menubutton(master = self.frame, height = 3, width = 70, text = 'Wybierz program do usunięcia', bg = 'white')
        self.menu = tk.Menu(master = self.menubutton)
        self.menubutton['menu'] = self.menu
        self.root = getroot(parent)
        with open(self.root.variables.jsonpath) as jsonfile:
            self.programs = json.load(jsonfile)
        for program in self.programs["Programs"]:
            self.menu.add_command(label = program['Name'], command = lambda obj = self, program = program['Name']: obj.command(program))
        self.menubutton.pack()
        self.frame.grid(column = 0, row = 0, columnspan = 3)
        self.buttonDoIt = ttk.Button(master = self, text = 'Usuń program', command = self._deleteprogram)
        self.buttonCancel = ttk.Button(master = self, text = 'Zaniechaj', command = self.cancel)
        self.buttonDoIt.grid(column = 0, row = 2, sticky = tk.W)
        self.buttonCancel.grid(column = 2, row = 2, sticky = tk.E)
        self.programtoDelete = {}
        self.center()

    def center(self):
        screenWidth = GetSystemMetrics(0)
        screenHeigth = GetSystemMetrics(1)
        size = tuple(int(val) for val in self.geometry().split('+')[0].split('x'))
        x = int(screenWidth/2 - size[0]/2)
        y = int(screenHeigth/2 - size[1]/2)
        self.geometry('+{}+{}'.format(x,y))

    def command(self, program = 'Pusty'):
        self.menubutton.config(text = program)
        for _program in self.programs['Programs']:
            if _program["Name"] == program:
                self.programtoDelete = _program
                break

    def createEmptyProgram(self):
        newprogram = {
            "Name":"New",
            "Table":[[0, 0, "", 0, 0, 0, 0, 0, 0]]
        }
        self.programs['Programs'].append(newprogram)

    def _deleteprogram(self):
        if self.programtoDelete:
            self.programs['Programs'].remove(self.programtoDelete)
            if not self.programs['Programs']:
                self.createEmptyProgram()
            with open(self.root.variables.jsonpath, 'w') as jsonfile:
                json.dump(self.programs, jsonfile)
            self.masterwidget.config(text = self.programs['Programs'][0]['Name'])
            self.root.variables.currentProgram = self.programs['Programs'][0]['Name']
            self.root.variables.internalEvents['TableRefresh'] = True
            self.root.variables.internalEvents['RefreshStartEnd'] = True
            self.root.variables.internalEvents['ProgramMenuRefresh'] = True
        prompt = AgainPrompt(master = self.master, cls = DeleteProgramWindow, args = (self.masterwidget,))
        prompt.grab_set()
        self.destroy()

    def cancel(self):
        self.destroy()

class AgainPrompt(tk.Toplevel):
    def __init__(self, master = None, cls = None, args = ()):
        super().__init__(master)
        self.title('Czy wykonać procedurę ponownie?')
        self.buttonDoIt = ttk.Button(self, text = 'Wykonaj ponownie', command = self.doitagain)
        self.buttonCancel = ttk.Button(self, text = 'Zaniechaj', command = self.cancel)
        self.Label = ttk.Label(master = self, text = "Czy wykonać procedurę ponownie?")
        self.Label.grid(column = 0, columnspan = 3, row = 0)
        self.buttonDoIt.grid(column = 0, row = 1)
        self.buttonCancel.grid(column = 2, row = 1)
        self.master = master
        self.args = args
        self.masterclass = cls
        self.center()

    def center(self):
        screenWidth = GetSystemMetrics(0)
        screenHeigth = GetSystemMetrics(1)
        size = tuple(int(val) for val in self.geometry().split('+')[0].split('x'))
        x = int(screenWidth/2 - size[0]/2)
        y = int(screenHeigth/2 - size[1]/2)
        self.geometry('+{}+{}'.format(x,y))

    def doitagain(self):
        masterclass = self.masterclass(self.master, *self.args)
        masterclass.grab_set()
        self.destroy()

    def cancel(self):
        self.destroy()

class StatusIndicators(dict):
    def __init__(self, master = None):
        super().__init__()
        self.frame = ttk.LabelFrame(master = master, text = 'Status')
        self.root = getroot(master)
        self.settings = master.settings['StatusIndicators']
        self.frame.__setattr__('settings', self.settings)
        self.widgets = []
        for key, indicator in self.settings.items():
            self.widgets.append(StatusIndicators.line(self.frame, label = indicator['Label'], indicator = key))
        for widget in self.widgets:
            widget.pack()
        self.pack()
    
    def update(self):
        self.frame.update()
        for widget in self.widgets:
            widget.update()
        
    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    class line(dict):
        def __init__(self, master = None, label = '', indicator = ''):
            super().__init__()
            self.key = indicator
            self.root = getroot(master)
            self.settings = master.settings[indicator]
            self.frame = ttk.Frame(master = master, **self.settings['Frame'])
            self.cwidth = self.settings['Frame']['height']
            self.place = self.cwidth//2
            self.frame.__setattr__('settings', self.settings)
            self.label = ttk.Label(self.frame)
            self.label.config(text=label)
            self.label.place(anchor='w', x='3', y=self.place)
            self.indicator = tk.Canvas(self.frame)
            self.indicator.config(background='Black', height=self.cwidth, width=self.cwidth, bd = 0)
            self.indicator.place(anchor='e', x=self.settings['Frame']['width'], y=self.place)
        
        def update(self):
            self.frame.update()
            self.indicator.config(bg = 'lightgreen' if self.root.variables.statusindicators[self.key]==1 else 'black' if self.root.variables.statusindicators[self.key]==0 else 'red' if self.root.variables.statusindicators[self.key]==-1 else 'blue')

        def pack(self, *args, **kwargs):
            self.frame.pack(*args, **kwargs)

class ProgramSelect(dict):
    def __init__(self, master = None):
        super().__init__()
        self.root = getroot(master)
        self.settings = master.settings['ProgramSelect']
        self.frame = ttk.LabelFrame(master = master, text = self.settings['Label'])
        self.menubutton = tk.Menubutton(master = self.frame, text = self.settings['Label'])
        self.frame.__setattr__('settings', self.settings)
        self.menu = None
        self.createmenu()

    def createmenu(self):
        if isinstance(self.menu, tk.Menu):
            self.menu.destroy()
        self.root.variables.jsonpath = str(Path(__file__).parent.absolute())+'\\Programs.json'
        with open(self.root.variables.jsonpath) as jsonfile:
            self.programs = json.load(jsonfile)
        self.menu = tk.Menu(master = self.menubutton, tearoff = 0)
        self.menubutton['menu'] = self.menu
        for program in self.programs["Programs"]:
            self.menu.add_command(label = program['Name'], command = lambda obj = self, program = program['Name']: obj.command(program))
        self.menu.add_command(label = 'Nowy program', command = self.newprogram)
        self.menu.add_command(label = 'Usuń program', command = self.deleteprogram)
        self.menubutton.pack()

    def newprogram(self):
        window = NewProgramWindow(self.frame, self.menubutton)
        window.grab_set()

    def deleteprogram(self):
        window = DeleteProgramWindow(self.frame, self.menubutton)
        window.grab_set()

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

    def update(self):
        self.frame.update()
        if self.root.variables.internalEvents['ProgramMenuRefresh']:
            self.createmenu()
            self.root.variables.internalEvents['ProgramMenuRefresh'] = False

class Positions(dict):
    def __init__(self, master = None):
        super().__init__()
        self.root = getroot(master)
        self.settings = master.settings['Positions']
        self.frame = ttk.LabelFrame(master = master, text = self.settings['Label'])
        self.frame.__setattr__('settings', self.settings)
        self.programs = json.load(open(self.root.variables.jsonpath))
        self.program = {}
        self.widgets = [
            ttk.Label(master = self.frame, text = self.settings['from']),
            ttk.Entry(master = self.frame, text = ''),
            ttk.Label(master = self.frame, text = self.settings['to']),
            ttk.Entry(master = self.frame, text = '')
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
        self.frame.update()
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

        
