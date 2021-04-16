import tkinter as tk
from tkinter import ttk
import json
from .common import Button, Window

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
