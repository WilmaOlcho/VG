import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json
from .Widgets import GeneralWidget, LabelFrame, Window, Button, getroot, KEYWORDS
from functools import reduce

class HomeScreen(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'HomeScreen')
        self.name = self.settings['Name']
        for key in self.settings.keys():
            if not key == 'Name':
                self.widgets.append(eval(key)(self))
        for widget in self.widgets:
            widget.pack(side = tk.LEFT, expand = tk.Y)
        self.pack(expand = tk.YES, fill=tk.BOTH)

class ThirdColumn(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'ThirdColumn')
        for key in self.settings:
            self.widgets.append(eval(key)(master = self))
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

class ProcessVariables(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'ProcessVariables')
        self.leftFrame = ttk.Frame(master = self)
        self.leftFrame.__setattr__('settings',self.settings)
        self.rightFrame = ttk.Frame(master = self)
        self.rightFrame.__setattr__('settings',self.settings)
        self.widgets.extend([self.leftFrame, self.rightFrame ])
        for key in self.settings['variablesFrame'].keys():
            self.widgets.append(variablesFrame(master = self.leftFrame, key = key))
        for key in self.settings['Button'].keys():
            button = tk.Button(master = self.rightFrame, font = self.font(), command = lambda obj = self, k = key: obj.click(k), **self.settings['Button'][key])
            button.__setattr__('settings',self.settings['interactive'][key])
            self.widgets.append(button)
        for widget in self.widgets:
            widget.pack(side = tk.LEFT if isinstance(widget, ttk.Frame) else tk.TOP, fill ='x', anchor = tk.N)
        self.pack()

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
        for widget in self.widgets:
            widget.update()
            if isinstance(widget, tk.Button):
                if 'condition' in widget.settings.keys():
                    condition = eval(widget.settings['condition'])
                    if condition:
                        widget.config(widget.settings['active'])
                    else:
                        widget.config(widget.settings['inactive'])
        super().update()

class variablesFrame(GeneralWidget):
    def __init__(self, master = None, key = 'auto'):
        super().__init__(master = master, branch = 'variablesFrame')
        self.key = key
        self.label = ttk.Label(master = self, text = self.settings[self.key]['Label'])
        self.entry = ttk.Entry(master = self, text = self.root.variables[self.key], width = self.settings[self.key]['width'])
        self.entry._name = self.key
        self.widgets.extend([self.label, self.entry])
        for widget in self.widgets:
            widget.pack(side = tk.TOP)
        self.pack()

    def update(self):
        for widget in self.widgets:
            if widget == self.entry:
                value = widget.get()
                expected = self.root.variables[self.key]
                if value != expected:
                    widget.delete(0,tk.END)
                    widget.insert(0,expected)
            widget.update()
        super().update()

class SecondColumn(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'SecondColumn')
        self.widgets.append(StatusIndicators(master = self))
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

class FirstColumn(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'FirstColumn')
        self.widgets.extend([
            ProgramSelect(self),
            Positions(self)
        ])
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

class NewProgramWindow(Window):
    def __init__(self, parent, menubuttonwidget):
        super().__init__(parent, branch = "NewProgram")
        self.masterwidget = menubuttonwidget
        self.menubutton = tk.Menubutton(master = self, relief = 'ridge', height = 3, width = 70, text = 'Wybierz program bazowy', bg = 'white')
        self.menu = tk.Menu(master = self.menubutton)
        self.menubutton['menu'] = self.menu
        with open(self.root.variables.jsonpath) as jsonfile:
            self.programs = json.load(jsonfile)
        self.menu.add_command(label = 'Pusty', command = self.command)
        for program in self.programs["Programs"]:
            self.menu.add_command(label = program['Name'], command = lambda obj = self, program = program['Name']: obj.command(program))
        self.menubutton.grid(columnspan = 3)
        self.nameentry = tk.Entry(master = self, text = "Nazwa nowego programu")
        self.nameentry.bind('<FocusIn>', self.nameentryclicked)
        self.nameentry.bind('<FocusOut>', self.nameentryreleased)
        self.NameentryLabel = ttk.Label(master = self, text = "Nazwa dla nowego programu")
        self.NameentryLabel.grid(column = 0, row = 1)
        self.nameentry.grid(column = 1, columnspan = 2, row= 1)
        self.newprogram = {}
        self.name = ''
        self.center()
        for button in self.settings['buttons']:
            self.widgets.append(Button(master = self, text = self.settings['buttons'][button]['text'], callback = lambda obj = self, btn = button: obj.ButtonClick(btn)))
            self.widgets[-1].grid(**self.settings['buttons'][button]['grid'])


    def ButtonClick(self, button):
        if button == "DoIt":
            self._newprogram()
        if button == "Cancel":
            self.cancel()

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

class DeleteProgramWindow(Window):
    def __init__(self, parent, menubuttonwidget):
        super().__init__(parent, branch = 'DeleteProgram')
        self.masterwidget = menubuttonwidget
        self.menubutton = tk.Menubutton(master = self, relief = 'ridge', height = 3, width = 70, text = 'Wybierz program do usunięcia', bg = 'white')
        self.menu = tk.Menu(master = self.menubutton)
        self.menubutton['menu'] = self.menu
        with open(self.root.variables.jsonpath) as jsonfile:
            self.programs = json.load(jsonfile)
        for program in self.programs["Programs"]:
            self.menu.add_command(label = program['Name'], command = lambda obj = self, program = program['Name']: obj.command(program))
        self.menubutton.grid(column = 0, row = 0, columnspan = 3)
        self.programtoDelete = {}
        self.center()
        for button in self.settings['buttons']:
            self.widgets.append(Button(master = self, text = self.settings['buttons'][button]['text'], callback = lambda obj = self, btn = button: obj.ButtonClick(btn)))
            self.widgets[-1].grid(**self.settings['buttons'][button]['grid'])


    def ButtonClick(self, button):
        if button == "DoIt":
            self._deleteprogram()
        if button == "Cancel":
            self.cancel()

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
        prompt = AgainPrompt(master = self.parent, cls = DeleteProgramWindow, args = (self.masterwidget,))
        prompt.grab_set()
        self.destroy()

    def cancel(self):
        self.destroy()

class AgainPrompt(Window):
    def __init__(self, master = None, cls = None, args = ()):
        super().__init__(master, branch = "AgainPrompt")
        self.Label = ttk.Label(master = self, text = "Czy wykonać procedurę ponownie?")
        self.Label.grid(column = 0, columnspan = 3, row = 0)
        self.args = args
        self.masterclass = cls
        self.center()
        for button in self.settings['buttons']:
            self.widgets.append(Button(master = self, text = self.settings['buttons'][button]['text'], callback = lambda obj = self, btn = button: obj.ButtonClick(btn)))
            self.widgets[-1].grid(**self.settings['buttons'][button]['grid'])

    def ButtonClick(self, button):
        if button == "DoIt":
            self.doitagain()
        if button == "Cancel":
            self.cancel()

    def doitagain(self):
        masterclass = self.masterclass(self.master, *self.args)
        masterclass.grab_set()
        self.destroy()

    def cancel(self):
        self.destroy()

class StatusIndicators(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'StatusIndicators')
        for key, indicator in self.settings.items():
            if key in KEYWORDS: continue
            self.widgets.append(StatusIndicators.line(self, label = indicator['Label'], indicator = key))
        for widget in self.widgets:
            widget.pack()
        self.pack()

    class line(GeneralWidget):
        def __init__(self, master = None, label = '', indicator = ''):
            super().__init__(master = master, branch = indicator)
            self.key = indicator
            self.config(**self.settings['Frame'])
            self.cwidth = self.settings['Frame']['height']
            self.place = self.cwidth//2
            self.__setattr__('settings', self.settings)
            self.label = ttk.Label(self)
            self.label.config(text=label)
            self.label.place(anchor='w', x='3', y=self.place)
            self.indicator = tk.Canvas(self)
            self.indicator.config(background='Black', height=self.cwidth, width=self.cwidth, bd = 0)
            self.indicator.place(anchor='e', x=self.settings['Frame']['width'], y=self.place)
        
        def update(self):
            self.indicator.config(bg = 'lightgreen' if self.root.variables.statusindicators[self.key]==1 else 'black' if self.root.variables.statusindicators[self.key]==0 else 'red' if self.root.variables.statusindicators[self.key]==-1 else 'blue')
            super().update()

class ProgramSelect(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'ProgramSelect')
        self.menubutton = tk.Menubutton(master = self, text = self.settings['Label'])
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
        window = NewProgramWindow(self, self.menubutton)
        window.grab_set()

    def deleteprogram(self):
        window = DeleteProgramWindow(self, self.menubutton)
        window.grab_set()

    def loadprogramminmax(self, program):
        minimum = reduce(lambda x,y: (x[1] if isinstance(x,list) else x) if (x[1] if isinstance(x,list) else x) <= y[1] else y[1], program['Table'])
        maximum = reduce(lambda x,y: (x[1] if isinstance(x,list) else x) if (x[1] if isinstance(x,list) else x) >= y[1] else y[1], program['Table'])
        return (minimum, maximum)

    def command(self, program):
        self.menubutton.config(text = program)
        self.root.variables.currentProgram = program
        for prog in self.programs['Programs']:
            if prog['Name'] == program:
                minimum, maximum = self.loadprogramminmax(prog)
                self.root.variables.programposstart = minimum
                self.root.variables.programposend = maximum
                break
        self.root.variables.internalEvents['RefreshStartEnd'] = True
        self.root.variables.internalEvents['TableRefresh'] = True

    def update(self):
        if self.root.variables.internalEvents['ProgramMenuRefresh']:
            self.createmenu()
            self.root.variables.internalEvents['ProgramMenuRefresh'] = False
        if self.root.variables.internalEvents['start']:
            self.menubutton.config(state = 'disabled')
        if self.root.variables.internalEvents['stop']:
            self.menubutton.config(state = 'normal')
        super().update()

class Positions(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'Positions')
        with open(self.root.variables.jsonpath, 'r') as jsonfile:
            self.programs = json.load(jsonfile)
        self.program = {}
        self.widgets = [
            ttk.Label(master = self, text = self.settings['from']),
            ttk.Entry(master = self, text = ''),
            ttk.Label(master = self, text = self.settings['to']),
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
        if self.root.variables.internalEvents['start']:
            for widget in self.widgets: widget.config(state = 'disabled')
        if self.root.variables.internalEvents['stop']:
            for widget in self.widgets: widget.config(state = 'normal')
        super().update()