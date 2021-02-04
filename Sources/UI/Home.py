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
            ProgramSelect(self, variables = self.variables),
            Positions(self, variables = self.variables)
        ]
        for widget in self.widgets:
            widget.pack(side = tk.LEFT, expand = tk.Y, fill ='both')
        self.pack()

class ProgramSelect(tk.Menubutton):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master, text = 'Program', relief = 'groove')
        self.variables = variables
        self.path = str(Path(__file__).parent.absolute())+'\\Programs.json'
        self.programs = json.load(open(self.path))
        self.menu = tk.Menu(master = self, tearoff = 0)
        self['menu'] = self.menu
        for program in self.programs["Programs"]:
            self.menu.add_command(label = program['Name'], command = lambda obj = self, program = program['Name']: obj.command(program))

    def command(self, program):
        self.config(text = program)
        self.variables.currentProgram = program

class Positions(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master, relief = 'groove')
        self.variables = variables
        self.widgets = [
            tk.Label(self, text = 'Wybór pozycji'),
            [
            tk.Label(self, text = 'OD '),
            tk.Entry(self, text = str(self.variables.programposstart)),
            tk.Label(self, text = 'DO '),
            tk.Entry(self, text = str(self.variables.programposend))]
        ]
        for widget in self.widgets:
            if isinstance(widget, list):
                self.widgets.append(tk.LabelFrame(self))
                for subwidget in widget:
                    subwidget.master = self.widgets[::-1][0]
                    if 'entry' in subwidget._name:
                        subwidget.config(width = 5)
                        subwidget.bind("<FocusOut>",lambda x, obj = self: obj.setvalue())
                    subwidget.pack(side = tk.LEFT)
                frame = self.widgets[::-1][0]
                frame.pack()
            else:
                widget.pack()
        self.pack()
        
    def setvalue(self):
        for widget in self.widgets:
            if isinstance(widget, list):
                for subwidget in widget:
                    if 'entry' in subwidget._name:
                        subwidget.update_idletasks()
                        if '2' in subwidget._name:
                            self.variables.programposend = subwidget.get()
                        else:
                            self.variables.programposstart = subwidget.get()
        
