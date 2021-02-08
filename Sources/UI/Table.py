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
        self.menu = self.CreateContextMenu()
        self.variables = variables
        self.master = master
        self.freeze = False
        self.table = []
        self.entries = []
        self.synctable = []
        self.focused_on = [0,0]
        self.width = 20
        self.tjson = json.load(open(self.variables.jsonpath))

    def CreateContextMenu(self):
        menu = tk.Menu(self, tearoff = 0)
        menu.add_command(label = "Dodaj wiersz przed", command = self.AddRowBefore)
        menu.add_command(label = "Dodaj wiersz za", command = self.AddRowAfter)
        menu.add_command(label = "Usuń wiersz", command = self.DeleteRow)
        menu.add_separator()
        menu.add_command(label = "Sortuj Tabelę", command = self.SortTable)
        return menu

    def ContextMenuPopup(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.menu.grab_release()

    def GetFocus(self, event):
        focus = self.focus_get()
        for row, row_content in enumerate(self.entries):
            for column, entry in enumerate(row_content):
                if isinstance(entry, tk.Entry):
                    if entry == focus:
                        entry.config(bg='lightblue')
                        self.focused_on = [row,column]
                    else: entry.config(bg='white')

    def getActiveRow(self):
        return self.focused_on[0]

    def CreateID(self):
        ID = 0
        for program in self.tjson['Programs']:
            if program['Name'] == self.variables.currentProgram:
                IDChanged = True
                while IDChanged:
                    IDChanged = False
                    for content in program['Table']:
                        if ID == content[0]:
                            ID += 1
                            IDChanged = True
        return ID


    def AddRowBefore(self):
        row = self.getActiveRow()
        self.synctable.insert(row,[self.CreateID(),0,0,0,0,0,0,0,0])
        self.UpdateJson()
        self.variables.internalEvents['TableRefresh'] = True

    def AddRowAfter(self):
        row = self.getActiveRow()
        self.synctable.insert(row+1,[self.CreateID(),0,0,0,0,0,0,0,0])
        self.UpdateJson()
        self.variables.internalEvents['TableRefresh'] = True

    def DeleteRow(self):
        row = self.getActiveRow()
        del self.synctable[row]
        self.UpdateJson()
        self.variables.internalEvents['TableRefresh'] = True

    def SortTable(self):
        self.synctable[0] = [0,0,0,0,0,0,0,0,0]
        self.synctable.sort(key = lambda element: element[1])
        self.UpdateJson()
        self.variables.internalEvents['TableRefresh'] = True

    def update(self):
        super().update()
        self.freeze = not self.variables.internalEvents['TableRefresh']
        if not self.freeze:
            for program in self.tjson['Programs']:
                if program['Name'] == self.variables.currentProgram:
                    self.frame.destroy()
                    self.frame = tk.Frame(self)
                    self.frame.pack()
                    self.table = [[0,0,0,0,0,0,0,0,0]].copy()
                    self.table.extend(program['Table'])
                    self.synctable = []
                    for row in self.table:
                        self.entries.append([None,None,None,None,None,None,None,None,None].copy())
                        self.synctable.append(row.copy())
                    break
            for row, content in enumerate(self.table):
                for column, value in enumerate(content):
                    if self.variables.displayedprogramcolumns[column]:
                        entry = tk.Entry(self.frame, width = self.variables.columnwidths[column])
                        self.entries[row][column] = entry
                        self.entries[row][column].delete(0,tk.END)
                        if row == 0:
                            self.entries[row][column].insert(0,self.variables.programcolumns[column])
                            self.entries[row][column].configure(state = 'disabled')
                        else:
                            self.entries[row][column].insert(0,value)
                            if column == 1 and isinstance(value, str): value = int(value)
                            self.synctable[row][column] = value 
                            self.entries[row][column].bind('<FocusOut>',self.RetrieveSynctable)
                            self.entries[row][column].bind('<FocusIn>',self.GetFocus)
                            self.entries[row][column].bind('<Button-3>',self.ContextMenuPopup)
                        self.entries[row][column].grid(row = row, column = column)
            self.freeze = True
            self.variables.internalEvents['TableRefresh'] = False
            self.variables.displayedprogramtableheight = (self.width * len(self.table)) - len(self.table)
            print(self.variables.displayedprogramtableheight)
            self.pack(expand = tk.YES, fill=tk.BOTH)
            return True
        if self.variables.internalEvents['DumpProgramToFile']:
            self.WriteSyncTable()
            self.variables.internalEvents['DumpProgramToFile'] = False
        return False
    
    def RetrieveSynctable(self, event):
        for row, content in enumerate(self.entries):
            for column, value in enumerate(content):
                if value:
                    tmp = value.get()
                    self.synctable[row][column] = tmp

    def UpdateJson(self):
        for i, program in enumerate(self.tjson['Programs']):
            if program['Name'] == self.variables.currentProgram:
                self.tjson['Programs'][i]['Table'] = []
                self.tjson['Programs'][i]['Table'] = self.synctable[1:].copy()
                break

    def WriteSyncTable(self):
        self.UpdateJson()
        json.dump(self.tjson,open(self.variables.jsonpath,'w'))
