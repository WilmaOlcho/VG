import tkinter as tk
from tkinter import ttk
from .Widgets.ScrolledTable import ScrolledWidget, PosTable
from .Widgets import getroot, GeneralWidget, NewProgramWindow, DeleteProgramWindow
import json

class TableScreen(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'TableScreen')
        self.name = 'Tabela programu'
        self.table = ScrolledWidget(PosTable, master = self)
        self.table.grid(columnspan = 5, sticky = 'E')
        for button in self.settings["Buttons"]:
            tk.Button(master = self, command = lambda v = self, settings = button: v.btnclick(settings), text = button['Label']).grid(**button['grid'])
    
    def btnclick(self, settings):
        if settings['action']=='save':
            self.root.variables.internalEvents['DumpProgramToFile'] = True
        if settings['action']=='new':
            window = NewProgramWindow(self, self.table)
            window.grab_set()
        if settings['action']=='delete':
            window = DeleteProgramWindow(self, self.table)
            window.grab_set()
