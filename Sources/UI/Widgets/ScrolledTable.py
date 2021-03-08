import tkinter as tk
import json
from . import getroot

class ScrolledWidget(dict):
    def __init__(self, widgetCls, text = '', master = None, height = 600, scrolltype = 'both'):
        super().__init__()
        self.root = getroot(master)
        self.settings = master.settings['ScrolledWidget']
        self.frame = tk.LabelFrame(master = master, **self.settings['LabelFrame'])
        self.frame.__setattr__('settings',self.settings)
        self.width, self.height = 0, self.root.variables.displayedprogramtableheight
        self.widgetheight = self.settings['LabelFrame']['height']
        for i, state in enumerate(self.root.variables.displayedprogramcolumns):
            if state: self.width += (self.root.variables.columnwidths[i]*6)
        self.frame['width'] = self.width
        self.frame.pack(expand = tk.N)
        self.cnv = tk.Canvas(master = self.frame, width = self.width, height = self.widgetheight)
        self.cnv.__setattr__('settings',self.settings)
        self.xscrollbar = tk.Scrollbar(master = self.frame, orient='horizontal', command = self.cnv.xview) if self.settings['scrolltype'] in ['h', 'horizontal', 'x', 'xy', 'yx', 'both'] else False
        self.yscrollbar = tk.Scrollbar(master = self.frame, orient='vertical', command = self.cnv.yview) if self.settings['scrolltype'] in ['v', 'vertical', 'y', 'xy', 'yx', 'both'] else False
        if self.xscrollbar:
            self.cnv.configure(xscrollcommand=self.xscrollbar.set)
            self.xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        if self.yscrollbar:
            self.cnv.configure(yscrollcommand=self.yscrollbar.set)
            self.yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cnv.pack(expand = tk.YES, fill = tk.BOTH)
        self.container = tk.Frame(master= self.cnv, width = self.width, height = self.widgetheight)
        self.container.__setattr__('settings',self.settings)
        self.content = widgetCls(master = self.container)
        self.container.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
        self.intid1 = self.cnv.create_window((0,0),window = self.container, anchor = tk.NW )
        self.cnv.config(scrollregion = (0,0,self.width, self.widgetheight), highlightthickness = 0)

    def update(self):
        if self.content.update():
            self.height = self.root.variables.displayedprogramtableheight
            self.container.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
            self.cnv.itemconfig(self.intid1, window = self.container)        
            self.cnv.config(scrollregion = (0,0,self.width,self.height), highlightthickness = 0)
            self.cnv.xview_moveto(0)
            self.cnv.yview_moveto(0)
        self.frame.update()
        
    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

class PosTable(dict):
    def __init__(self, master = None):
        super().__init__()
        self.master = master
        self.frame = tk.Frame(master = self.master)
        self.root = getroot(master)
        self.settings = master.settings['PosTable']
        self.frame.__setattr__('settings', self.settings)
        self.freeze = False
        self.menu = self.CreateContextMenu()
        self.table = []
        self.program = []
        self.entries = []
        self.synctable = []
        self.focused_on = [0,0]
        self.width = 20
        with open(self.root.variables.jsonpath, 'r') as jsonfile:
            self.tjson = json.load(jsonfile)

    def CreateContextMenu(self):
        menu = tk.Menu(self.frame, tearoff = 0)
        for element in self.settings['ContextMenu']:
            if 'separator' in element:
                menu.add_separator()
            if 'command' in element:
                menu.add_command(label = element['label'], command = eval(element['command']))
        return menu

    def ContextMenuPopup(self, event):
        self.frame.update_idletasks()
        try:
            self.menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.menu.grab_release()

    def GetFocus(self, event):
        self.frame.update_idletasks()
        focus = self.frame.focus_get()
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
        self.frame.update_idletasks()
        row = self.getActiveRow()
        self.synctable.insert(row,[self.CreateID(),0,0,0,0,0,0,0,0])
        self.UpdateJson()
        while self.root.variables.internalEvents['TableRefresh']: pass #wait until previous change is done
        self.root.variables.internalEvents['TableRefresh'] = True

    def AddRowAfter(self):
        self.frame.update_idletasks()
        row = self.getActiveRow()
        self.synctable.insert(row+1,[self.CreateID(),0,0,0,0,0,0,0,0])
        self.UpdateJson()
        while self.root.variables.internalEvents['TableRefresh']: pass #wait until previous change is done
        self.root.variables.internalEvents['TableRefresh'] = True

    def DeleteRow(self):
        self.frame.update_idletasks()
        row = self.getActiveRow()
        del self.synctable[row]
        self.UpdateJson()
        while self.root.variables.internalEvents['TableRefresh']: pass #wait until previous change is done
        self.root.variables.internalEvents['TableRefresh'] = True

    def SortTable(self):
        self.frame.update_idletasks()
        def sortconditions(element):
            value = int(element[1]) if str(element[1]).isnumeric() else 0
            return value
        self.synctable.sort(key = sortconditions)
        self.UpdateJson()
        while self.root.variables.internalEvents['TableRefresh']: pass #wait until previous change is done
        self.root.variables.internalEvents['TableRefresh'] = True

    def __reframe(self):
        self.frame.destroy()
        self.frame = tk.Frame(master = self.master)
        self.menu = self.CreateContextMenu()
        self.frame.__setattr__('settings', self.settings)
        self.frame.pack()

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
        entry = tk.Entry(self.frame, width = self.root.variables.columnwidths[column])
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
        self.root.variables.internalEvents['TableRefresh'] = False
        tableheight = (self.width * len(self.table)) - len(self.table)
        self.root.variables.displayedprogramtableheight = tableheight
        self.pack(expand = tk.YES, fill=tk.BOTH)

    def update(self):
        self.frame.update()
        self.freeze = not self.root.variables.internalEvents['TableRefresh']
        if not self.freeze:
            self.TableChanged()
            return True
        if self.root.variables.internalEvents['DumpProgramToFile']:
            self.WriteSyncTable()
        return False
    
    def RetrieveSynctable(self, event):
        self.frame.update_idletasks()
        for row, content in enumerate(self.entries):
            for column, value in enumerate(content):
                if value: self.synctable[row][column] = value.get()

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

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)