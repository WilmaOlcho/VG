import tkinter as tk
from tkinter import ttk
from Variables import Variables
import json

class TableScreen(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.master = master
        self.name = 'Table'
        self.widgets = [
            PosTable(self, variables=self.variables)
        ]
        for widget in self.widgets:
            widget.pack(fill = 'both', expand = tk.Y)
        self.pack()
    
    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class PosTable(tk.LabelFrame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.master = master
        self.freeze = False
        self.table = []
        self.entries = []

    def update(self):
        super().update()
        self.freeze = not self.variables.internalEvents['TableRefresh']
        if not self.freeze:
            tjson = json.load(open(self.variables.jsonpath))
            for program in tjson['Programs']:
                if program['Name'] == self.variables.currentProgram:
                    self.table = program['Table']
                    self.entries = len(self.table)*[9*[[]]]
                    break
            for row, content in enumerate(self.table):
                for column, value in enumerate(content):
                    self.entries[row][column] = tk.Entry(self)
                    self.entries[row][column].delete(0,tk.END)
                    self.entries[row][column].insert(0,value)
                    
                    self.entries[row][column].grid(row = row, column = column)
            self.freeze = True
            self.variables.internalEvents['TableRefresh'] = False
            self.pack()


