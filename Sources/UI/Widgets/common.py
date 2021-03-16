import tkinter as tk
from tkinter import ttk
from win32api import GetSystemMetrics

KEYWORDS = ["Label"]

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
        for widget in self.widgets:
            widget.update()

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

    def update(self):
        focus = self.focus_get()
        if focus != self.entry:
            value = self.root.variables[self.masterkey][self.key]
            if self.entry.get() != value:
                self.entry.delete(0,tk.END)
                self.entry.insert(0,value)

class Lamp(GeneralWidget):
    def __init__(self, master = None, text = '', key = ''):
        super().__init__(master = master, branch = 'Lamp')
        self.config(**self.settings['frame'])
        self.lamp = tk.Canvas(master = self, width = self.settings['width'], height = self.settings['height'])
        self.caption = ttk.Label(master = self, text = text, **self.settings['caption'])
        self.key = key
        self.masterkey = self.settings['masterkey']
        self.caption.pack(side = tk.LEFT)
        self.lamp.pack(side = tk.LEFT)
        self.lit = False

    def update(self):
        super().update()
        keystartpos = 0
        negation = '-' in self.key[:2]
        if negation: keystartpos += 1
        errsign = '!' in self.key[:2]
        if errsign: keystartpos += 1
        key = self.key[keystartpos:]
        if negation:
            self.lit = not self.root.variables[self.masterkey][key]
        else:
            self.lit = self.root.variables[self.masterkey][key]
        if errsign:
            self.lamp.config(bg = self.settings['Color']['error'] if self.lit else self.settings['Color']['normal'])
        else:
            self.lamp.config(bg = self.settings['Color']['active'] if self.lit else self.settings['Color']['normal'])

class Window(GeneralWidget, tk.Toplevel):
    def __init__(self, parent = None, branch = ''):
        #self.toplevel = tk.Toplevel( master = parent)
        #self.toplevel.__setattr__('settings', parent.settings)
        #self.parent = parent
        #super().__init__(master = self.toplevel, branch = branch)
        #self.toplevel.title(self.settings['title'])
        GeneralWidget.__init__(self, master = parent, branch = branch)
        tk.Toplevel.__init__(self, master = parent)
        self.title = self.settings['title']

    def center(self):
        screenWidth = GetSystemMetrics(0)
        screenHeigth = GetSystemMetrics(1)
        size = tuple(int(val) for val in self.geometry().split('+')[0].split('x'))
        x = int(screenWidth/2 - size[0]/2)
        y = int(screenHeigth/2 - size[1]/2)
        self.geometry('+{}+{}'.format(x,y))

