import tkinter as tk
from tkinter import ttk
from .common import Window, Button

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
