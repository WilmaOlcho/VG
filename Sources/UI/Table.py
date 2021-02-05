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
            ScrolledWidget(PosTable, text = 'Tabela programu:', variables=self.variables, master = self)
                    ]
        for widget in self.widgets:
            widget.pack(fill = 'both', expand = tk.Y)
        self.pack()
    
    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

#Działa nie tykać
class ScrolledWidget(tk.LabelFrame):
    def __init__(self, widgetCls, text = '', master = None, variables = Variables(), height = 600, scrolltype = 'both'):
        self.variables = variables
        self.master = master
        self.width, self.height = 0, self.variables.displayedprogramtableheight
        for i, state in enumerate(self.variables.displayedprogramcolumns):
            if state: self.width += (self.variables.columnwidths[i]*6)
        super().__init__(master = master, text = text, width = self.width, height = height)
        self.pack(expand = tk.N)
        self.cnv = tk.Canvas(master = self, width = self.width, height = height)
        self.xscrollbar = tk.Scrollbar(master = self, orient='horizontal', command = self.cnv.xview) if scrolltype in ['h', 'horizontal', 'x', 'xy', 'yx', 'both'] else False
        self.yscrollbar = tk.Scrollbar(master = self, orient='vertical', command = self.cnv.yview) if scrolltype in ['v', 'vertical', 'y', 'xy', 'yx', 'both'] else False
        if self.xscrollbar:
            self.cnv.configure(xscrollcommand=self.xscrollbar.set)
            self.xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        if self.yscrollbar:
            self.cnv.configure(yscrollcommand=self.yscrollbar.set)
            self.yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cnv.pack(expand = tk.YES, fill = tk.BOTH)
        self.container = tk.Frame(master= self.cnv, width = self.width, height = height)
        self.content = widgetCls(master = self.container, variables =  self.variables)
        self.container.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
        self.intid1 = self.cnv.create_window((0,0),window = self.container, anchor = tk.NW )
        self.cnv.config(scrollregion = (0,0,self.width, height), highlightthickness = 0)

    def update(self):
        if self.content.update():
            self.height = self.variables.displayedprogramtableheight
            self.container.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
            self.cnv.itemconfig(self.intid1, window = self.container)        
            self.cnv.config(scrollregion = (0,0,self.width,self.height), highlightthickness = 0)
            self.cnv.xview_moveto(0)
            self.cnv.yview_moveto(0)
        super().update()
        

class PosTable(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.frame = tk.Frame(self)
        self.variables = variables
        self.master = master
        self.freeze = False
        self.table = []
        self.entries = []
        self.width = 20

    def update(self):
        super().update()
        self.freeze = not self.variables.internalEvents['TableRefresh']
        if not self.freeze:
            tjson = json.load(open(self.variables.jsonpath))
            for program in tjson['Programs']:
                if program['Name'] == self.variables.currentProgram:
                    self.frame.destroy()
                    self.frame = tk.Frame(self)
                    self.frame.pack()
                    self.table = [[0,0,0,0,0,0,0,0,0]]
                    self.table.extend(program['Table'])
                    self.entries = (len(self.table))*[9*[[]]]
                    break
            for row, content in enumerate(self.table):
                for column, value in enumerate(content):
                    if self.variables.displayedprogramcolumns[column]:
                        if row == 0:
                            self.entries[row][column] = tk.Entry(self.frame, width = self.variables.columnwidths[column])
                            self.entries[row][column].delete(0,tk.END)
                            self.entries[row][column].insert(0,self.variables.programcolumns[column])
                            self.entries[row][column].configure(state = 'disabled')
                            self.entries[row][column].grid(row = row, column = column)
                        else:
                            self.entries[row][column] = tk.Entry(self.frame, width = self.variables.columnwidths[column])
                            self.entries[row][column].delete(0,tk.END)
                            self.entries[row][column].insert(0,value)
                            self.entries[row][column].grid(row = row, column = column)
            self.freeze = True
            self.variables.internalEvents['TableRefresh'] = False
            self.variables.displayedprogramtableheight = (self.width * len(self.table)) - len(self.table)
            print(self.variables.displayedprogramtableheight)
            self.pack(expand = tk.YES, fill=tk.BOTH)
            return True
        return False

