import tkinter as tk
from tkinter import ttk
from .common import Frame, KEYWORDS
import re

class VariablesFrames(Frame):
    def __init__(self, master = None, side = tk.TOP):
        super().__init__(master = master, branch = 'VariablesFrames')
        for variablesframe in self.settings.keys():
            if variablesframe in KEYWORDS: continue
            if '!' in variablesframe[:1]:
                Vframe = VariablesFrame(self, entryclass = VariablesMenu, branch = variablesframe, side = side)
            else:    
                Vframe = VariablesFrame(self, branch = variablesframe, side = side)
            Vframe.pack(side = side)

class VariablesFrame(Frame):
    def __init__(self, master = None, entryclass = tk.Entry, branch = 'VariablesFrame', side = tk.TOP):
        super().__init__(master = master, branch = branch)
        self.key = branch
        self.label = ttk.Label(master = self, text = self.settings['Label'])
        self.entry = entryclass(master = self)
        if isinstance(self.entry, tk.Entry):
            self.entry.config(width = self.settings['width'])
            self.entry.bind('<FocusOut>', self.valueUpdate)
        for widget in self.winfo_children():
            widget.pack(side = side)

    def valueUpdate(self, event):
        entry = event.widget
        self.root.variables[entry.master.key] = entry.get()

    def update(self):
        if isinstance(self.entry, tk.Entry):
            if not self.focus_get() == self.entry:
                value = self.entry.get()
                expected = self.root.variables[self.key]
                if value != expected:
                    if value:
                        self.entry.delete(0,tk.END)
                    self.entry.insert(tk.INSERT,expected)
        super().update()

class VariablesMenu(Frame):
    def __init__(self, master = None, branch = '', text = '', side = tk.TOP):
        super().__init__(master, branch = branch)
        self.key = branch
        self.menubutton = tk.Menubutton(self, relief = 'sunken', takefocus = 1, bg = 'white', text = text, width = self.settings['width'])
        self.menu = None
        self.itemsmasterkey, self.itemskey = self.settings['items'].split('.')
        self.variablemasterkey, self.variablekey = self.settings['variable'].split('.')
        self.changemasterkey, self.changekey = self.settings['changeevent'].split('.')
        self.items = self.root.variables[self.itemsmasterkey][self.itemskey]
        self.createmenu()

    def config(self, **kwargs):
        self.menubutton.config(**kwargs)

    def removefromstring(self, string, substring):
        searchresult = re.search(substring, string)
        if searchresult:
            newstring = ''
            for i, character in enumerate(string):
                if i in range(*searchresult.regs[0]): continue
                newstring += character
            return newstring
        return string

    def popupmenu(self, event):
        try:
            self.menubutton.focus_set()
            self.menubutton.event_generate('<<Invoke>>')
            #param = (event.widget.winfo_rootx(), event.widget.winfo_rooty(),event.widget.winfo_width(), event.widget.winfo_height())
            #self.menu.tk_popup(param[0]+param[2],param[1]+param[3], 0)
        finally:
            pass
            # self.menu.grab_release()

    def createmenu(self):
        if isinstance(self.menu, tk.Menu):
            self.menu.destroy()
        self.menu = tk.Menu(self.menubutton, tearoff = 0)
        self.menubutton['menu'] = self.menu
        for item in self.items:
            name = item
            if self.settings['notforlabel'] in name:
                name = self.removefromstring(name,self.settings['notforlabel'])
            self.menu.add_command(label = name, command = lambda obj = self, choice = name: obj.setvariable(choice))
        self.menubutton.pack()

    def update(self):
        #print(self.focus_get())
        text = self.root.variables[self.variablemasterkey][self.variablekey]
        text = self.removefromstring(text,self.settings['notforlabel'])
        items = self.root.variables[self.itemsmasterkey][self.itemskey]
        itemschanged = False
        if items != self.items:
            itemschanged = True
            self.items = items
        if self.menubutton.cget('text') != text or itemschanged:
            self.createmenu()
            self.menubutton.config(text = text)
        super().update()

    def setvariable(self, recipe):
        self.menubutton.configure(text = recipe)
        self.root.variables[self.variablemasterkey][self.variablekey] = recipe + self.settings['notforlabel']
        self.root.variables[self.changemasterkey][self.changekey] = True

