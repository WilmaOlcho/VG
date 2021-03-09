import tkinter as tk
from tkinter import ttk
from .Widgets import Font, LabelledScrolledText, getroot
import json
from pathlib import Path
from ..UI import SettingsScreen
from ..UI import HomeScreen
from ..UI import TableScreen
from ..UI import Variables

class Frame(dict):
    def __init__(self, master = None):
        self.frame = tk.Frame(master = master)
        dict.__init__(self)
        self.settings = master.settings['MainWindow']
        self.root = getroot(master)
        self.OverallNotebook = ttk.Notebook(self.frame, **self.settings['Notebook']['constructor'])
        self.OverallNotebook.__setattr__('settings',self.settings['Notebook'])
        self.widgets = [
            LabelledScrolledText(master = self.frame, **self.settings['ErrorTextArea']['constructor']),
            tk.Button(master = self.frame, font = self.root.font(), command = self.ack, **self.settings['ackbutton']['constructor']),
            HomeScreen(master = self.OverallNotebook),
            SettingsScreen(master = self.OverallNotebook),
            TableScreen(master = self.OverallNotebook) 
        ]
        col = 0
        for widget in self.widgets:
            if hasattr(widget, 'name'):
                self.OverallNotebook.add(widget.frame, text=widget.name)
            else:
                widget.grid(column = col, row=0, sticky = tk.NSEW)
                col +=1
        self.OverallNotebook.grid(**self.settings['Notebook']['grid'])
        self.frame.pack()

    def update(self):
        super().update()
        for widget in self.widgets:
            if isinstance(widget, tk.Button):
                widget.config(bg = 'red' if self.root.variables.internalEvents['error'] else 'yellow')
            widget.update()

    def ack(self):
        self.root.variables.internalEvents['ack'] = True

class Window(dict):
    def __init__(self, lockerinstance, settingsfile):
        super().__init__()
        self.window = tk.Tk()
        root = self.window
        settingsfile = str(Path(__file__).parent.absolute())+'//widgetsettings.json'
        with open(settingsfile) as jsonfile:
            widgetsettings = json.load(jsonfile)
        root.__setattr__('variables', Variables(lockerinstance, **widgetsettings))
        root.__setattr__('settings', root.variables['widgetsettings'])
        self.settings = root.settings
        root.__setattr__('font',Font(root = self.window, **self.settings['MainFont']))
        rootstyle = ttk.Style()
        rootstyle.configure('.',font = root.font())
        root.title(self.settings['title'])
        root.attributes('-fullscreen', True)
        self.widgets = [
            Frame(master = root)
        ]
        self.Alive = True
        self.loop()

    def loop(self):
        while self.Alive:
            self.window.update()
            for widget in self.widgets:
                widget.update()
            self.window.variables.update()
            self.Alive = self.window.variables.Alive

if __name__ == '__main__':
    filepath = str(Path(__file__).parent.absolute())+'//widgetsettings.json'
    Window(object, filepath)
    