import tkinter as tk
from tkinter import ttk
from .common import Frame, KEYWORDS

class VariablesFrames(Frame):
    def __init__(self, master = None, side = tk.TOP):
        super().__init__(master = master, branch = 'VariablesFrames')
        for variablesframe in self.settings.keys():
            if variablesframe in KEYWORDS: continue
            Vframe = VariablesFrame(self, branch = variablesframe, side = side)
            Vframe.pack(side = side)

class VariablesFrame(Frame):
    def __init__(self, master = None, branch = 'VariablesFrame', side = tk.TOP):
        super().__init__(master = master, branch = branch)
        self.key = branch
        self.label = ttk.Label(master = self, text = self.settings['Label'])
        self.entry = tk.Entry(master = self, width = self.settings['width'])
        for widget in self.winfo_children():
            widget.pack(side = side)

    def update(self):
        value = self.entry.get()
        expected = self.root.variables[self.key]
        if value != expected:
            if value:
                self.entry.delete(0,tk.END)
            self.entry.insert(tk.INSERT,expected)
        super().update()
