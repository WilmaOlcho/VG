import tkinter as tk
from tkinter import ttk
from Widgets import ScrolledWidget, PosTable
import json
from . import getroot

class TableScreen(dict):
    def __init__(self, master = None):
        super().__init__()
        self.root = getroot(master)
        self.settings = master.settings['TableScreen']
        self.frame = tk.Frame(master = master)
        self.name = 'Tabela programu'
        self.widgets = [
            ScrolledWidget(PosTable, master = self.frame),
            tk.Button(master = self.frame, command = lambda v = self: v.btnclick(), text = self.settings["Button"]["Label"])
                    ]
        for widget in self.widgets:
            widget.pack()
        self.pack(expand = tk.YES, fill=tk.BOTH)
    
    def update(self):
        self.frame.update()
        for widget in self.widgets:
            widget.update()

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def btnclick(self):
        self.root.variables.internalEvents['DumpProgramToFile'] = True

