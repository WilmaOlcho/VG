import tkinter as tk
from tkinter import ttk
from Variables import Variables
from Widgets.ScrolledTable import ScrolledWidget, PosTable
import json

class TableScreen(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.master = master
        self.name = 'Tabela programu'
        self.widgets = [
            ScrolledWidget(PosTable, text = 'Tabela programu:', variables=self.variables, master = self),
            tk.Button(master = self, command = lambda v = self: v.btnclick(), text = 'Zapisz')
                    ]
        for widget in self.widgets:
            widget.pack()
        self.pack()
    
    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

    def btnclick(self):
        self.variables.internalEvents['DumpProgramToFile'] = True

