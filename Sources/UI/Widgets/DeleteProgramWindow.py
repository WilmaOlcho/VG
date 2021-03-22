import tkinter as tk
import json
from .common import Window, Button
from .AgainPromptWindow import AgainPrompt

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
        prompt = AgainPrompt(master = self.master, cls = DeleteProgramWindow, args = (self.masterwidget,))
        prompt.grab_set()
        self.destroy()

    def cancel(self):
        self.destroy()