import tkinter as tk
from tkinter import ttk
from pathlib import Path
from Variables import Variables
import json

class HomeScreen(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.master = master
        self.name = 'home'
        self.widgets = [
            FirstColumn(self, variables = self.variables),
            SecondColumn(self, variables = self.variables),
            ThirdColumn(self, variables = self.variables)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.LEFT, expand = tk.Y)
        self.pack()

    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class ThirdColumn(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.master = master
        self.widgets = [
            ProcessVariables(self, variables = self.variables)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
        self.pack()

    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class ProcessVariables(tk.LabelFrame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master, text = 'Proces')
        self.variables = variables
        self.master = master
        self.leftFrame = tk.Frame(self)
        self.rightFrame = tk.Frame(self)
        self.widgets = [
            variablesFrame(master = self.leftFrame, text = 'Pozycja w tabeli', key = 'currentposition'),
            variablesFrame(master = self.leftFrame, text = 'Czas cyklu', key = 'processtime'),
            tk.Button(master = self.rightFrame, text = "Krok", command = self.stepclick),
            tk.Button(master = self.rightFrame, text = 'Uruchom', command = self.startclick),
            tk.Button(master = self.rightFrame, text = 'Zatrzymaj', command = self.stopclick),
            self.leftFrame,
            self.rightFrame
        ]
        for widget in self.widgets:
            widget.pack(side = tk.LEFT if widget.master == self else tk.TOP, fill ='x', anchor = tk.S)
        self.pack()

    def stepclick(self):
        self.variables.auto != self.variables.auto

    def startclick(self):
        self.variables.ProgramActive = True

    def stopclick(self):
        self.variables.ProgramActive = False

    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class variablesFrame(tk.Frame):
    def __init__(self, master = None, variables = Variables(), text = 'Pozycja w tabeli', key = 'auto'):
        super().__init__(master = master)
        self.variables = variables
        self.key = key
        self.master = master
        self.widgets = [
            tk.Label(master = self, text = text),
            tk.Entry(master = self, text = self.variables.ProcessVariables[self.key], width = 10)
        ]
        for widget in self.widgets:
            widget.pack()
        self.pack()

    def update(self):
        super().update()
        for widget in self.widgets:
            if isinstance(widget,tk.Entry):
                widget.delete(0,tk.END)
                widget.insert(0,self.variables.ProcessVariables[self.key])
            widget.update()


class SecondColumn(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.master = master
        self.widgets = [
            StatusIndicators(self, variables = self.variables)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.BOTTOM, fill ='x', anchor = tk.S)
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
        for prog in self.programs['Programs']:
            if prog['Name'] == program:
                self.variables.programposstart = min(int(item[1]) for item in prog['Table'])
                self.variables.programposend = max(int(item[1]) for item in prog['Table'])
                break
        self.variables.internalEvents['RefreshStartEnd'] = True
        self.variables.internalEvents['TableRefresh'] = True

class Positions(tk.LabelFrame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master, text = 'Wybór pozycji')
        self.variables = variables
        self.programs = json.load(open(self.variables.jsonpath))
        self.program = {}
        self.widgets = [
            tk.Label(master = self, text = 'OD '),
            tk.Entry(master = self, text = ''),
            tk.Label(master = self, text = 'DO '),
            tk.Entry(master = self, text = '')
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
                    self.variables.programposend = value
                else:
                    self.variables.programposstart = value
        self.variables.internalEvents['RefreshStartEnd'] = True


    def update(self):
        super().update()
        for program in self.programs['Programs']:
            if program['Name'] == self.variables.currentProgram:
                self.program = program
        if self.variables.internalEvents['RefreshStartEnd']:
            for widget in self.widgets:
                if 'entry' in widget._name:
                    widget.delete(0,tk.END)
                    if '2' in widget._name:
                        widget.insert(0,str(self.variables.programposend))
                    else:
                        widget.insert(0,str(self.variables.programposstart))
        self.variables.internalEvents['RefreshStartEnd'] = False

        
