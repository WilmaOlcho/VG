import tkinter as tk
from tkinter import ttk
from win32api import GetSystemMetrics
import re

KEYWORDS = ["Label","masterkey", "Name", "masterkey", "width", "height"]

def Blank(*args, **kwargs):
    return None

def getroot(obj):
    while True:
        if hasattr(obj, 'master'):
            if obj.master:
                obj = obj.master
            else:
                break
        else:
            break
    return obj

class GeneralWidget(tk.Frame):
    def __init__(self, master = None, branch = ''):
        tk.Frame.__init__(self, master)
        self.settings = master.settings[branch] if branch else master.settings
        self.root = getroot(master)
        self.widgets = []
        self.font = self.root.font
        self.master = master

    def update(self):
        super().update()
        for widget in list(self.children.values()): #winfo_children() returns full list of childrens, even if some of them are destroyed
            widget.update()

Frame = GeneralWidget

class LabelFrame(GeneralWidget, ttk.LabelFrame):
    def __init__(self, master = None, branch = ''):
        GeneralWidget.__init__(self, master = master, branch = branch)
        ttk.LabelFrame.__init__(self, master = master)
        self.widgetName = 'labelframe'
        self.config(text = self.settings['Label'])
    
class Button(GeneralWidget, tk.Button):
    def __init__(self, master = None, callback = Blank, text = '', key = ''):
        GeneralWidget.__init__(self, master = master, branch = 'Button')
        tk.Button.__init__(self, master = master, font = self.font(), text = text, command = self.click, width = self.settings['width'], height = self.settings['height'])
        self.key = key
        if key:
            self.masterkey = self.settings['masterkey']
        self.callback = callback

    def click(self):
        if self.key:
            if self.key[0] == '-':
                self.root.variables[self.masterkey][self.key[1:]] = False
            else:
                self.root.variables[self.masterkey][self.key] = True
        else:
            self.callback()

class Entry(GeneralWidget):
    def __init__(self, master = None, text = '', key = ''):
        super().__init__(master = master, branch = 'Entry')
        self.Label = ttk.Label(master = self, font = self.font(), text = text)
        self.entry = tk.Entry(master = self, width = self.settings['width'])
        self.entry.bind('<FocusOut>',self.ReadEntry)
        self.key = key
        self.masterkey = self.settings['masterkey']
        self.Label.pack()
        self.entry.pack()
        
    def ReadEntry(self, event):
        self.root.variables[self.masterkey][self.key] = self.entry.get()

    def WriteEntry(self):
        value = self.root.variables[self.masterkey][self.key]
        if self.entry.get() != value:
            self.entry.delete(0,tk.END)
            self.entry.insert(0,value)

    def update(self):
        focus = self.focus_get()
        if focus != self.entry:
            self.WriteEntry()
        super().update()

class Lamp(GeneralWidget):
    def __init__(self, master = None, branch = "Lamp"):
        super().__init__(master = master, branch = branch)
        self.config(**self.settings['frame'])
        self.key = branch
        self.lamp = tk.Canvas(master = self, width = self.settings['width'], height = self.settings['height'])
        self.caption = ttk.Label(master = self, text = self.settings['Label'], **self.settings['caption'])
        self.masterkey = master.settings['masterkey']
        self.caption.pack(side = tk.LEFT)
        self.lamp.pack(side = tk.LEFT)
        self.lit = False

    def update(self):
        super().update()
        keystartpos = 0
        negation = '-' in self.key[:3]
        if negation: keystartpos += 1
        errsign = '!' in self.key[:3]
        if errsign: keystartpos += 1
        highlight = '~' in self.key[:3]
        if highlight: keystartpos += 1
        key = self.key[keystartpos:]
        if negation:
            self.lit = not self.root.variables[self.masterkey][key]
        else:
            self.lit = self.root.variables[self.masterkey][key]
        if self.lit:
            if errsign:
                self.lamp.config(bg = self.settings['Color']['error'])
            elif highlight:
                self.lamp.config(bg = self.settings['Color']['highlighted'])
            else:
                self.lamp.config(bg = self.settings['Color']['active'])
        else:
            self.lamp.config(bg = self.settings['Color']['normal'])

class Window(GeneralWidget, tk.Toplevel):
    def __init__(self, parent = None, branch = ''):
        GeneralWidget.__init__(self, master = parent, branch = branch)
        tk.Toplevel.__init__(self, master = parent)
        self.destroyed = False
        if 'title' in self.settings:
            self.title(self.settings['title'])
        else:
            self.title(self._name)

    def destroy(self):
        self.destroyed = True
        super().destroy()

    def center(self):
        screenWidth = GetSystemMetrics(0)
        screenHeigth = GetSystemMetrics(1)
        size = tuple(int(val) for val in self.geometry().split('+')[0].split('x'))
        x = int(screenWidth/2 - size[0]/2)
        y = int(screenHeigth/2 - size[1]/2)
        self.geometry('+{}+{}'.format(x,y))

class RecipesMenu(Frame):
    def __init__(self, master = None, items = [], variable = '', settings = {}, text = '', side = tk.TOP):
        super().__init__(master, branch = '')
        if settings: self.settings = settings
        self.menubutton = tk.Menubutton(self, relief = 'sunken', bg = 'white', text = text)
        self.menu = None
        self.items = items
        self.variable = variable
        self.createmenu()
        for widget in self.winfo_children():
            widget.pack(side = side, fill = 'both')

    def createmenu(self):
        if isinstance(self.menu, tk.Menu):
            self.menu.destroy()
        self.menu = tk.Menu(self.menubutton, tearoff = 0)
        self.menubutton['menu'] = self.menu
        for item in self.items:
            self.menu.add_command(label = item, command = lambda obj = self, choice = item: obj.setvariable(choice))
        self.menubutton.pack(expand = 1, fill = 'both')

    def update(self):
        self.menubutton.config(text = self.variable)
        super().update()

    def setvariable(self, recipe):
        self.menubutton.configure(text = recipe)
        self.variable = recipe

    def get(self):
        return self.variable

    def delete(self, *args, **kwargs):
        pass

    def insert(self, index, value, *args, **kwargs):
        self.variable = value
    
