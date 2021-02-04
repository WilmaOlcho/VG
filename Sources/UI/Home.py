import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from Variables import Variables

class HomeScreen(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.master = master
        self.name = 'home'
        self.widgets = [
            FirstColumn(self, variables = self.variables),
            StatusIndicators(self, variables = self.variables)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.LEFT, expand = tk.Y)
        self.pack()

    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class FirstColumn(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.master = master
        self.widgets = [
            ProgramSelect(self, variables = self.variables),
            Positions(self, variables = self.variables)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class StatusIndicators(tk.LabelFrame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master, text = 'Status')
        self.variables = variables
        self.widgets = [
            StatusIndicators.line(self, variables = self.variables, label = 'Bezpieczeństwo:', indicator = 'Safety'),
            StatusIndicators.line(self, variables = self.variables, label = 'Gaz osłonowy:', indicator = 'ShieldingGas'),
            StatusIndicators.line(self, variables = self.variables, label = 'Filtrowentylator:', indicator = 'VacuumFilter'),
            StatusIndicators.line(self, variables = self.variables, label = 'Powietrze:', indicator = 'Air'),
            StatusIndicators.line(self, variables = self.variables, label = 'Krosdżet:', indicator = 'Crossjet'),
            StatusIndicators.line(self, variables = self.variables, label = 'Wózek', indicator = 'Troley'),
            StatusIndicators.line(self, variables = self.variables, label = 'Oświetlenie:', indicator = 'Light'),
            StatusIndicators.line(self, variables = self.variables, label = 'Robot', indicator = 'Robot')
        ]
        for widget in self.widgets:
            widget.pack()
        self.pack()
    
    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

    class line(tk.Frame):
        def __init__(self, master = None, variables = Variables(), label = '', indicator = ''):
            super().__init__(master = master, height='15', width='150')
            self.key = indicator
            self.variables = variables
            self.label = tk.Label(self)
            self.label.config(text=label)
            self.label.place(anchor='w', x='3', y='5')
            self.indicator = tk.Canvas(self)
            self.indicator.config(background='Black', height='10', width='10')
            self.indicator.place(anchor='e', x='120', y='5')
            self.pack()
        
        def update(self):
            super().update()
            self.indicator.config(bg = 'lightgreen' if self.variables.statusindicators[self.key]==1 else 'black' if self.variables.statusindicators[self.key]==0 else 'red')

class ProgramSelect(tk.LabelFrame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master, text = 'Program')
        self.menubutton = tk.Menubutton(master = self, text = 'Program')
        self.variables = variables
        self.variables.jsonpath = str(Path(__file__).parent.absolute())+'\\Programs.json'
        self.programs = json.load(open(self.variables.jsonpath))
        self.menu = tk.Menu(master = self.menubutton, tearoff = 0)
        self.menubutton['menu'] = self.menu
        for program in self.programs["Programs"]:
            self.menu.add_command(label = program['Name'], command = lambda obj = self, program = program['Name']: obj.command(program))
        self.menubutton.pack()

    def command(self, program):
        self.menubutton.config(text = program)
        self.variables.currentProgram = program
        self.variables.programposstart = 1
        for prog in self.programs['Programs']:
            if prog['Name'] == program:
                self.variables.programposend = len(prog['Table'])-1
                break
        self.variables.internalEvents['RefreshStartEnd'] = True
        self.variables.internalEvents['TableRefresh'] = True

class Positions(tk.LabelFrame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master, text = 'Wybór pozycji')
        self.variables = variables
        self.widgets = [
            tk.Label(self, text = 'OD '),
            tk.Entry(self, text = str(self.variables.programposstart)),
            tk.Label(self, text = 'DO '),
            tk.Entry(self, text = str(self.variables.programposend))
        ]
        for widget in self.widgets:
            if 'entry' in widget._name:
                widget.config(width = 5)
                widget.bind("<FocusOut>",lambda x, obj = self: obj.setvalue())
            widget.pack(side = tk.LEFT, anchor = tk.N)
        self.pack()
        
    def setvalue(self):
        for widget in self.widgets:
            if isinstance(widget, list):
                if 'entry' in widget._name:
                    widget.update_idletasks()
                    if '2' in widget._name:
                        self.variables.programposend = widget.get()
                    else:
                        self.variables.programposstart = widget.get()

    def update(self):
        super().update()
        if self.variables.internalEvents['RefreshStartEnd']:
            for widget in self.widgets:
                if 'entry' in widget._name:
                    widget.delete(0,tk.END)
                    if '2' in widget._name:
                        widget.insert(0,str(self.variables.programposend))
                    else:
                        widget.insert(0,str(self.variables.programposstart))
            self.variables.internalEvents['RefreshStartEnd'] = False
        
        
