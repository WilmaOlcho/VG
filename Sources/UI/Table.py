import tkinter as tk
from tkinter import ttk
from .Widgets.ScrolledTable import ScrolledWidget, PosTable
from .Widgets import getroot, GeneralWidget
import json

class TableScreen(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'TableScreen')
        self.name = 'Tabela programu'
        self.widgets = [
            ScrolledWidget(PosTable, master = self),
            tk.Button(master = self, command = lambda v = self: v.btnclick(), text = self.settings["Button"]["Label"])
                    ]
        for widget in self.widgets:
            widget.pack()

    def btnclick(self):
        self.root.variables.internalEvents['DumpProgramToFile'] = True

