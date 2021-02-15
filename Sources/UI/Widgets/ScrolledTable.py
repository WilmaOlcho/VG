import tkinter as tk
import json
from . import getroot

class ScrolledWidget(tk.LabelFrame):
    def __init__(self, widgetCls, text = '', master = None, height = 600, scrolltype = 'both'):
        self.root = getroot(master)
        self.master = master
        self.width, self.height = 0, self.root.variables.displayedprogramtableheight
        for i, state in enumerate(self.root.variables.displayedprogramcolumns):
            if state: self.width += (self.root.variables.columnwidths[i]*6)
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
        self.content = widgetCls(master = self.container)
        self.container.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
        self.intid1 = self.cnv.create_window((0,0),window = self.container, anchor = tk.NW )
        self.cnv.config(scrollregion = (0,0,self.width, height), highlightthickness = 0)

    def update(self):
        if self.content.update():
            self.height = self.root.variables.displayedprogramtableheight
            self.container.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
            self.cnv.itemconfig(self.intid1, window = self.container)        
            self.cnv.config(scrollregion = (0,0,self.width,self.height), highlightthickness = 0)
            self.cnv.xview_moveto(0)
            self.cnv.yview_moveto(0)
        super().update()
        

class PosTable(dict):
    def __init__(self, master = None):
        super().__init__()
        self.frame = tk.Frame(self)
        self.menu = self.CreateContextMenu()
        self.root = getroot(master)
        self.settings = master.settings['PosTable']
        self.frame.__setattr__('settings', self.settings)
        self.freeze = False
        self.table = []
        self.program = []
        self.entries = []
        self.synctable = []
        self.focused_on = [0,0]
        self.width = 20
        self.tjson = json.load(open(self.root.variables.jsonpath))

    def CreateContextMenu(self):
        menu = tk.Menu(self.frame, tearoff = 0)
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
        row = self.getActiveRow()
        self.synctable.insert(row,[self.CreateID(),0,0,0,0,0,0,0,0])
        self.UpdateJson()
        self.root.variables.internalEvents['TableRefresh'] = True

    def AddRowAfter(self):
        row = self.getActiveRow()
        self.synctable.insert(row+1,[self.CreateID(),0,0,0,0,0,0,0,0])
        self.UpdateJson()
        self.root.variables.internalEvents['TableRefresh'] = True

    def DeleteRow(self):
        row = self.getActiveRow()
        del self.synctable[row]
        self.UpdateJson()
        self.root.variables.internalEvents['TableRefresh'] = True

    def SortTable(self):
        self.synctable.sort(key = lambda element: element[1] if isinstance(element[1],int) else 0)
        self.UpdateJson()
        self.root.variables.internalEvents['TableRefresh'] = True

    def __reframe(self):
        self.frame.destroy()
        self.frame = tk.Frame(self)
        self.menu['master'] = self.frame
        self.frame.__setattr__('settings', self.settings)
        self.frame.pack()

    def __getprogram(self, i = False):
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
        for row, content in enumerate(self.entries):
            for column, value in enumerate(content):
                if value: self.synctable[row][column] = value.get()

    def UpdateJson(self):
        i = self.__getprogram(i = 'only')
        self.tjson['Programs'][i]['Table'] = []
        self.tjson['Programs'][i]['Table'] = self.synctable[1:].copy()

    def WriteSyncTable(self):
        self.UpdateJson()
        json.dump(self.tjson,open(self.root.variables.jsonpath,'w'))
        self.root.variables.internalEvents['DumpProgramToFile'] = False

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)