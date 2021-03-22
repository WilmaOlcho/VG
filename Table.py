import tkinter as tk

class jsonimport(dict):
    def __init__(self, filepath):
        super().__init__()

class csvimport(dict):
    def __init__(self, filepath):
        super().__init__()

class __BasicSettings(dict):
    def __init__(self):
        super().__init__()
        self['ContextMenu'] = [
            "separator",
            {"Label":"NewlineUP", "command":"self.createnewlineUP"},
            {"Label":"NewlineDOWN", "command":"self.createnewlineDOWN"},
            {"Label":"DeleteLine", "command":"self.deleteline"},
            {"Label":"Sort", "command":"self.sorttable"},
            "separator"
        ]

class PosTable(tk.Frame):
    def __init__(self, **kwargs):
        self.acceptableargs = ('columns', 'rows', 'file', 'table', 'settings', 'master')
        self.checkkwargs(kwargs)
        super().__init__(master = kwargs['master'])
        
        if 'settings' in kwargs:
            self.settings = kwargs.pop('settings')
        else:
            self.settings = __BasicSettings()

        self.freeze = False
        self.menu = self.CreateContextMenu()
        self.table = []
        self.entries = []
        self.synctable = []
        self.focused_on = [0,0]
        self.width = 20

    def checkkwargs(self, kwargs):
        for arg in kwargs.keys():
            if not arg in self.acceptableargs:
                raise TypeError('argument {} is not acceptable'.format(arg))

    def CreateContextMenu(self):
        menu = tk.Menu(master = self, tearoff = 0)
        for element in self.settings['ContextMenu']:
            if 'separator' in element:
                menu.add_separator()
            if 'command' in element:
                menu.add_command(label = element['label'], command = eval(element['command']))
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
        program = self.__getprogram()
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

    def AddRowAfter(self):
        row = self.getActiveRow()
        self.synctable.insert(row+1,[self.CreateID(),0,0,0,0,0,0,0,0])
        self.UpdateJson()

    def DeleteRow(self):
        row = self.getActiveRow()
        del self.synctable[row]
        self.UpdateJson()

    def SortTable(self):
        def sortconditions(element):
            value = int(element[1]) if str(element[1]).isnumeric() else 0
            return value
        self.synctable.sort(key = sortconditions)
        self.UpdateJson()

    def __reframe(self):
        for child in list(self.children.values()):
            child.destroy()
        self.menu = self.CreateContextMenu()
        self.pack()

    def __getprogram(self, i = False):
        with open(self.root.variables.jsonpath, 'r') as jsonfile:
            compareinput = json.load(jsonfile)
        if len(self.tjson['Programs']) != len(compareinput['Programs']):
            self.tjson = compareinput
        for j, program in enumerate(self.tjson['Programs']):
            if program['Name'] == self.root.variables.currentProgram:
                if i:
                    if isinstance(i, str):
                        if i == 'only':
                            return j
                        return False
                    else:
                        return j, program
                else:
                    return program
        return self.blankprogram

    def __resetTable(self):
        self.table = [[0,0,0,0,0,0,0,0,0]].copy()
        self.table.extend(self.program['Table'])
        self.synctable = []
        self.entries = []
        for row in self.table:
            self.entries.append([None,None,None,None,None,None,None,None,None].copy())
            self.synctable.append(row.copy())
    
    def __bindEvents(self, row, column):
        self.entries[row][column].bind('<FocusOut>',self.RetrieveSynctable)
        self.entries[row][column].bind('<FocusIn>',self.GetFocus)
        self.entries[row][column].bind('<Button-3>',self.ContextMenuPopup)

    def __createnameentry(self, row, column):
        self.entries[row][column].insert(0,self.root.variables.programcolumns[column])
        self.entries[row][column].configure(state = 'disabled')

    def __createnormalnentry(self, row, column, value):
        self.entries[row][column].insert(0,value)
        if column == 1 and isinstance(value, str): value = int(value)
        self.synctable[row][column] = value
        self.__bindEvents(row, column)
        
    def __entry(self, row, column, value):
        entry = tk.Entry(self, width = self.root.variables.columnwidths[column])
        self.entries[row][column] = entry
        self.entries[row][column].delete(0,tk.END)
        if row == 0:
            self.__createnameentry(row, column)
        else:
            self.__createnormalnentry(row, column, value)
        self.entries[row][column].grid(row = row, column = column)

    def __createnewtable(self):
        for row, content in enumerate(self.table):
            for column, value in enumerate(content):
                if self.root.variables.displayedprogramcolumns[column]:
                    self.__entry(row, column, value)

    def TableChanged(self):
        self.program = self.__getprogram()
        self.__reframe()
        self.__resetTable()
        self.__createnewtable()
        self.pack(expand = tk.YES, fill=tk.BOTH)

    def configentries(self, **cfg):
        table = self.entries[1:]
        def reduct(x, y):
            if x: 
                x = x.copy() #some work for GC, but it prevents from changing self.entries lists
                if y: x.extend(y) 
                return x
            else: return y
        entries = reduce(reduct, table, [])
        while None in entries: entries.remove(None)
        for entry in entries: entry.config(**cfg) #I've no idea why map doesn't work in this case

    def update(self):
        super().update()
        self.freeze = not self.root.variables.internalEvents['TableRefresh']
        if self.recipes != self.root.variables['scout']['recipes']: self.freeze = False
        if not self.freeze:
            self.recipes = self.root.variables['scout']['recipes']
            self.TableChanged()
            return True
        if self.root.variables.internalEvents['DumpProgramToFile']:
            self.WriteSyncTable()
        if self.root.variables.internalEvents['start']:
            self.configentries(state = 'disabled')
        if self.root.variables.internalEvents['stop']:
            self.configentries(state = 'normal')
        return False
    
    def RetrieveSynctable(self, event):
        if isinstance(event, tk.Event):
            widget = event.widget
        else:
            widget = event
        for row, content in enumerate(self.entries):
            for column, value in enumerate(content):
                if value == widget:
                    changedvariable = value.get()
                    if self.root.variables.columntypes[column] == type('') or isinstance(self.root.variables.columntypes[column],str):
                        self.synctable[row][column] = changedvariable
                        return
                    if self.root.variables.columntypes[column] == type(1):
                        if changedvariable.isnumeric():
                            self.synctable[row][column] = int(changedvariable)
                        else:
                            value.delete(0,tk.END)
                            value.insert(0,self.synctable[row][column])
                        return

    def UpdateJson(self):
        i = self.__getprogram(i = 'only')
        self.tjson['Programs'][i]['Table'] = []
        self.tjson['Programs'][i]['Table'] = self.synctable[1:].copy()
        pass

    def WriteSyncTable(self):
        self.UpdateJson()
        with open(self.root.variables.jsonpath, 'w') as jsonfile:
            json.dump(self.tjson,jsonfile)
        self.root.variables.internalEvents['DumpProgramToFile'] = False
