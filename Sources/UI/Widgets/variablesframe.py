import tkinter as tk
from tkinter import ttk
from .common import Frame

class VariablesFrames(Frame):
    def __init__(self, master = None, key = 'auto', side = tk.TOP):
        super().__init__(master = master, branch = 'variablesFrames')
        for variablesframe in self.settings.keys():
            Vframe = VariablesFrame(self, branch = variablesframe, key = key, side = side)
            Vframe.pack(side = side)

class VariablesFrame(Frame):
    def __init__(self, master = None, branch = 'VariablesFrame', key = 'auto', side = tk.TOP):
        super().__init__(master = master, branch = branch)
        self.key = key
        self.label = ttk.Label(master = self, text = self.settings[self.key]['Label'])
        self.entry = tk.Entry(master = self, width = self.settings[self.key]['width'])
        self.widgets.extend([self.label, self.entry])
        for widget in self.widgets:
            widget.pack(side = side)

    def update(self):
        value = self.entry.get()
        expected = self.root.variables[self.key]
        if value != expected:
            if value:
                self.entry.delete(0,tk.END)
            self.entry.insert(tk.INSERT,expected)
        super().update()
