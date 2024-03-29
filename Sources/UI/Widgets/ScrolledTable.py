import tkinter as tk
import json
from .common import LabelFrame, GeneralWidget, getroot, Menu
from functools import reduce

class ScrolledWidget(LabelFrame):
    def __init__(self, widgetCls, text = '', master = None, height = 600, scrolltype = 'both'):
        super().__init__(master = master, branch = "ScrolledWidget")
        self.width, self.height = 0, self.root.variables.displayedprogramtableheight
        self.widgetheight = self.settings['LabelFrame']['height']
        for i, state in enumerate(self.root.variables.displayedprogramcolumns):
            if state: self.width += (self.root.variables.columnwidths[i]*6)
        self['width'] = self.width
        self.cnv = tk.Canvas(master = self, height = self.widgetheight)
        self.cnv.__setattr__('settings',self.settings)
        self.xscrollbar = tk.Scrollbar(master = self, orient='horizontal', command = self.cnv.xview) if self.settings['scrolltype'] in ['h', 'horizontal', 'x', 'xy', 'yx', 'both'] else False
        self.yscrollbar = tk.Scrollbar(master = self, orient='vertical', command = self.cnv.yview) if self.settings['scrolltype'] in ['v', 'vertical', 'y', 'xy', 'yx', 'both'] else False
        if self.xscrollbar:
            self.cnv.configure(xscrollcommand=self.xscrollbar.set)
            self.xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        if self.yscrollbar:
            self.cnv.configure(yscrollcommand=self.yscrollbar.set)
            self.yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.width += 25
        self.cnv.config(width = self.width)
        self.pack(expand = tk.N)
        self.cnv.pack(expand = tk.YES, fill = tk.BOTH)
        self.container = tk.Frame(master= self.cnv)
        self.container.__setattr__('settings',self.settings)
        self.content = widgetCls(master = self.container)
        self.container.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
        self.intid1 = self.cnv.create_window((0,0),window = self.container, anchor = tk.NW )
        self.cnv.config(scrollregion = (0,0,self.width, self.widgetheight), highlightthickness = 0)
        self.cnv.bind_all("<MouseWheel>", self._mousescrolling)


    def _mousescrolling(self, event):
        self.cnv.yview_scroll(int(-1*(event.delta/120)), "units")


    def update(self):
        if self.content.update():
            self.height = self.root.variables.displayedprogramtableheight
            self.container.pack(side = tk.LEFT, expand = tk.YES, fill = tk.BOTH)
            self.cnv.itemconfig(self.intid1, window = self.container)        
            self.cnv.config(scrollregion = self.cnv.bbox('all'), highlightthickness = 0)
            self.cnv.bind_all("<MouseWheel>", self._mousescrolling)
            if self.cget('text')!=self.root.variables.currentProgram:
                self.config(text=self.root.variables.currentProgram)
        super().update()

class PosTable(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = "PosTable")
        self.freeze = False
        self.menu = self.CreateContextMenu()
        self.table = []
        self.program = []
        self.entries = []
        self.synctable = []
        self.blankprogram = {
            "Name":"",
            "Table":[[0,0,'',0,0,0,0,'',0]]
        }
        self.visibleColumns = []
        for i, val in enumerate(self.root.variables.displayedprogramcolumns):
            if val: self.visibleColumns.append(i)
        self.focused_on = [0,0]
        self.width = 20
        self.recipes = self.root.variables['scout']['recipes']
        with open(self.root.variables.jsonpath, 'r') as jsonfile:
            self.tjson = json.load(jsonfile)


    def ChangeFocus(self, event = '', column = 0, row = 0, type = 'inc'):
        if event:
            button = event.keysym
            if button == 'Up':
                row = -1
            elif button == 'Down':
                row = 1
            elif button == 'Left':
                column = -1
            elif button == 'Right':
                column = 1
        currentcolumn = self.visibleColumns.index(self.focused_on[1])
        currentrow = self.focused_on[0] 
        if type == 'inc':
            if currentcolumn + column > len(self.visibleColumns)-1:
                currentcolumn -= len(self.visibleColumns)
                currentcolumn += column
            elif currentcolumn + column < 0:
                currentcolumn += len(self.visibleColumns) + column
            else:
                currentcolumn += column
            if currentrow + row > len(self.table) - 1:
                currentrow -= len(self.table)
                currentrow += row
                if currentrow == 0:
                    currentrow = 1
            elif currentrow + row <= 0:
                if currentrow == 0: currentrow = len(self.table) - 1
                else: currentrow += len(self.table) + row - 1
            else:
                currentrow += row
            

            self.focused_on[1] = self.visibleColumns[currentcolumn]
            self.focused_on[0] = currentrow
        else:
            self.focused_on[1] = column
            self.focused_on[0] = row
        self.entries[self.focused_on[0]][self.focused_on[1]].focus_set()
        self.GetFocus(self.entries[self.focused_on[0]][self.focused_on[1]])


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

    def GetFocus(self, event='', focus = None):
        if not focus:
            focus = self.focus_get()
        for row, row_content in enumerate(self.entries):
            for column, entry in enumerate(row_content):
                if entry:
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
        while self.root.variables.internalEvents['TableRefresh']: pass #wait until previous change is done
        self.root.variables.internalEvents['TableRefresh'] = True


    def AddRowAfter(self):
        row = self.getActiveRow()
        self.synctable.insert(row+1,[self.CreateID(),0,0,0,0,0,0,0,0])
        self.UpdateJson()
        while self.root.variables.internalEvents['TableRefresh']: pass #wait until previous change is done
        self.root.variables.internalEvents['TableRefresh'] = True


    def DeleteRow(self):
        row = self.getActiveRow()
        del self.synctable[row]
        self.UpdateJson()
        while self.root.variables.internalEvents['TableRefresh']: pass #wait until previous change is done
        self.root.variables.internalEvents['TableRefresh'] = True


    def SortTable(self):
        def sortconditions(element):
            value = int(element[1]) if str(element[1]).isnumeric() else 0
            return value
        self.synctable.sort(key = sortconditions)
        self.UpdateJson()
        while self.root.variables.internalEvents['TableRefresh']: pass #wait until previous change is done
        self.root.variables.internalEvents['TableRefresh'] = True


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
        widget = self.entries[row][column]
        self.unbind_all('<Button-3>')
        widget.bind('<FocusOut>',self.RetrieveSynctable)
        widget.bind('<FocusIn>',self.GetFocus)
        if not isinstance(widget, tk.Entry):
            def popup(event, widget = widget):
                if widget.cget('state') == "normal":
                    try:
                        widget.menu.tk_popup(widget.winfo_rootx(), widget.winfo_rooty(), 0)
                    finally:
                        widget.menu.grab_release()
            widget.menubutton.bind('<ButtonRelease-3>',lambda event, _=self: [_.ChangeFocus(event,row=row, column = column,type = 'abs'), _.ContextMenuPopup(event)])
            widget.menubutton.bind('<Button-1>',lambda event, _=self: _.ChangeFocus(event,row=row, column = column,type = 'abs'))
            widget.bind('<space>', popup)
            widget.bind('<Up>',self.ChangeFocus)
            widget.bind('<Down>',self.ChangeFocus)
            widget.bind('<Left>',self.ChangeFocus)
            widget.bind('<Right>',self.ChangeFocus)
        else:
            widget.bind('<ButtonRelease-3>',lambda event, _=self: [_.ChangeFocus(event,row=row, column = column,type = 'abs'), _.ContextMenuPopup(event)])
            widget.bind('<Up>',self.ChangeFocus)
            widget.bind('<Down>',self.ChangeFocus)
            widget.bind('<Left>',self.ChangeFocus)
            widget.bind('<Right>',self.ChangeFocus)


    def __createnameentry(self, row, column):
        self.entries[row][column].insert(0,self.root.variables.programcolumns[column])
        self.entries[row][column].configure(state = 'disabled')


    def __createnormalnentry(self, row, column, value):
        self.entries[row][column].insert(0,value)
        if column == 1 and isinstance(value, str): value = int(value)
        self.synctable[row][column] = value
        self.__bindEvents(row, column)
        

    def __entry(self, row, column, value):
        sticky = tk.NS
        if row != 0 and self.root.variables.columntypes[column] == 'MENU':
            entry = Menu(self, width = self.root.variables.columnwidths[column], callback = self.RetrieveSynctable, items = self.recipes)
            sticky = tk.EW
        elif row != 0 and self.root.variables.columntypes[column] == 'PROMPTMENU':
            entry = Menu(self, width = self.root.variables.columnwidths[column], callback = self.RetrieveSynctable, items = ["Nie","Tak"])
            sticky = tk.EW
        else:
            entry = tk.Entry(self, justify = tk.CENTER, width = self.root.variables.columnwidths[column])
        self.entries[row][column] = entry
        self.entries[row][column].delete(0,tk.END)
        if row == 0:
            self.__createnameentry(row, column)
        else:
            self.__createnormalnentry(row, column, value)
        self.entries[row][column].grid(row = row, column = column, sticky = sticky)


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
            self.root.variables.internalEvents['TableRefresh'] = False
            return True
        if self.root.variables.internalEvents['DumpProgramToFile']:
            self.WriteSyncTable()
        if self.root.variables.internalEvents['start']:
            self.configentries(state = 'disabled')
        if self.root.variables.internalEvents['stop']:
            self.configentries(state = 'normal')
        return True
    

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
        self.tjson['Programs'][i]['Table'] = self.synctable[1:].copy()
        pass


    def WriteSyncTable(self):
        self.UpdateJson()
        with open(self.root.variables.jsonpath, 'w') as jsonfile:
            json.dump(self.tjson,jsonfile)
        self.root.variables.internalEvents['DumpProgramToFile'] = False

