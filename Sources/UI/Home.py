import tkinter as tk
from tkinter import ttk
import json
from .Widgets import VariablesFrames, StatusIndicators, GeneralWidget
from .Widgets import LabelFrame, KEYWORDS, Button, Entry
from .Widgets import Frame, DeleteProgramWindow, NewProgramWindow
from functools import reduce

class HomeScreen(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'HomeScreen')
        self.name = self.settings['Name']
        for key in self.settings.keys():
            if key not in KEYWORDS:
                eval(key)(self)
        for widget in self.winfo_children():
            widget.pack(side = tk.LEFT, expand = tk.Y)

class ThirdColumn(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'ThirdColumn')
        for key in self.settings:
            if key not in KEYWORDS:
                eval(key)(self)
        for widget in self.winfo_children():
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        for widget in self.winfo_children():
            widget.bind('<Button-1>',lambda event:event.widget.focus_set())



class ProcessVariables(LabelFrame):
    def __init__(self, master = None, **kwargs):
        super().__init__(master = master, branch = 'ProcessVariables')
        self.leftFrame = Frame(self)
        self.rightFrame = Frame(self)
        vframes = VariablesFrames(self.leftFrame, side = tk.TOP)
        vframes.pack(side = tk.TOP)
        for key in self.settings['Button'].keys():
            button = tk.Button(self.rightFrame, font = self.font(), **self.settings['Button'][key])
            button.__setattr__('settings',self.settings['interactive'][key])
            button.config(command = lambda obj = self, k = key, btn = button: obj.click(k, btn))
            button.pack(side = tk.TOP)
        for widget in self.winfo_children():
            widget.pack(side = tk.LEFT, fill ='x', anchor = tk.N)

    def click(self, key, button):
        if 'action' in button.settings:
            action = button.settings['action']
            anticondition = eval(button.settings['anticondition']) if 'anticondition' in button.settings else False
            if action == key and not anticondition:
                result = button.settings['result'].split('\n')
                for line in result:
                    if '=' in line:
                        exec(line)
                    else:
                        eval(line)

    def update(self):
        for widget in self.rightFrame.winfo_children():
            if isinstance(widget, tk.Button):
                if 'condition' in widget.settings.keys():
                    condition = eval(widget.settings['condition'])
                    if condition:
                        widget.config(widget.settings['active'])
                    else:
                        widget.config(widget.settings['inactive'])
        super().update()

class SecondColumn(GeneralWidget):
    def __init__(self, master = None, **kwargs):
        super().__init__(master = master, branch = 'SecondColumn')
        StatusIndicators(master = self)
        for widget in self.winfo_children():
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)

class FirstColumn(GeneralWidget):
    def __init__(self, master = None, **kwargs):
        super().__init__(master = master, branch = 'FirstColumn')
        ProgramSelect(self),
        Positions(self)
        for widget in self.winfo_children():
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)

class ProgramSelect(LabelFrame):
    def __init__(self, master = None, **kwargs):
        super().__init__(master = master, branch = 'ProgramSelect')
        self.menubutton = tk.Menubutton(master = self, text = self.settings['Label'])
        self.menu = None
        self.createmenu()

    def createmenu(self):
        if isinstance(self.menu, tk.Menu):
            self.menu.destroy()
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

    def loadprogramminmax(self, program): #I love this function, it's look beautiful
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
        if self.root.variables['ProgramActive']:
            self.menubutton.config(state = 'disabled')
        if self.root.variables['ProgramActive']:
            self.menubutton.config(state = 'normal')
        super().update()

class Positions(LabelFrame):
    def __init__(self, master = None, **kwargs):
        super().__init__(master = master, branch = 'Positions')
        with open(self.root.variables.jsonpath, 'r') as jsonfile:
            self.programs = json.load(jsonfile)
        self.program = {}
        self.refreshlock = True
        self.widgets = [
            ttk.Label(master = self, text = self.settings['from']),
            Entry(master = self, text = '', key = "programposstart"),
            ttk.Label(master = self, text = self.settings['to']),
            Entry(master = self, text = '', key = "programposend")
        ]
        for widget in self.widgets:
            if isinstance(widget, Entry):
                widget.config(width = 5)
            widget.pack(side = tk.LEFT, anchor = tk.N)
        self.pack()
        
    def nearest(self, value, attempts = list()):
        attemptlist = attempts.copy()
        attemptlist.sort(key = lambda element, v = int(value): abs(v - int(element)))
        import tkinter.messagebox as messagebox #simplicity for a while
        messagebox.showwarning('Co ty wyprawiasz!?','Podana wartość nie występuje w tablicy,\n    automatycznie poprawiono na:\n              {}'.format(attemptlist[0]))
        return attemptlist[0]

    def setvalue(self, widget):
            altered = False
            if isinstance(widget, tk.Entry):
                value = widget.get()
                if not value.isnumeric(): return None
                value = int(value)
                positionsintable = [item[1] for item in self.program['Table']]
                if not value in positionsintable:
                    value = self.nearest(value, positionsintable)
                if '2' in widget._name:
                    altered |= self.root.variables.programposend != value
                    self.root.variables.programposend = value
                else:
                    altered |= self.root.variables.programposstart != value
                    self.root.variables.programposstart = value
            if altered:
                self.root.variables.internalEvents['RefreshStartEnd'] = True
        
    def update(self):
        for program in self.programs['Programs']:
            if program['Name'] == self.root.variables.currentProgram:
                self.program = program
        anychange = False
        for widget in self.widgets:
            widget.update()
            
        #    if widget != self.focus_get():
        #        if hasattr(widget, 'flag'):
        #            if widget.flag:
        #                widget.flag = False
        #                self.setvalue(widget)
        #        if self.root.variables.internalEvents['RefreshStartEnd']:
        #            if 'entry' in widget._name:
        #                expected = str(self.root.variables.programposend if '2' in widget._name else self.root.variables.programposstart)
        #                if widget.get() != expected:
        ##                    anychange = True
        #                    widget.delete(0,tk.END)
        #                    widget.insert(0,expected)
        #    else: 
        #        widget.__setattr__('flag',True)
        #        self.root.variables.internalEvents['RefreshStartEnd'] = True
        #if not anychange: self.root.variables.internalEvents['RefreshStartEnd'] = False
        if self.root.variables['ProgramActive']:
            for widget in self.widgets: widget.config(state = 'disabled')
        else:
            for widget in self.widgets: widget.config(state = 'normal')
        super().update()
