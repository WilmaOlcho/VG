import tkinter as tk
from tkinter import ttk
from .Widgets import Font, LabelledScrolledText, getroot, GeneralWidget
import json
from pathlib import Path
from ..UI import SettingsScreen
from ..UI import HomeScreen
from ..UI import TableScreen
from ..UI import Variables

class Notebook(GeneralWidget, ttk.Notebook):
    def __init__(self, master = None, branch = "Notebook"):
        GeneralWidget.__init__(self, master, branch = branch)
        ttk.Notebook.__init__(self, master, **self.settings['constructor'])

class Frame(GeneralWidget):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'MainWindow')
        self.OverallNotebook = Notebook(self)
        self.notificationsarea = LabelledScrolledText(self, **self.settings['ErrorTextArea']['constructor'])
        self.ackbutton = tk.Button(self, font = self.root.font(), command = self.ack, **self.settings['ackbutton']['constructor'])
        screens = [
            HomeScreen(master = self.OverallNotebook),
            SettingsScreen(master = self.OverallNotebook),
            TableScreen(master = self.OverallNotebook) ]
        for screen in screens:
            self.OverallNotebook.add(screen, text=screen.settings['Name'])
        self.notificationsarea.grid(column = 0, row=0, sticky = tk.NSEW)
        self.ackbutton.grid(column = 1, row =0, sticky = tk.NSEW)
        self.OverallNotebook.grid(**self.settings['Notebook']['grid'])

    def update(self):
        start = self.root.variables.internalEvents['start']
        stop = self.root.variables.internalEvents['stop']
        super().update()
        self.ackbutton.config(bg = 'red' if self.root.variables.internalEvents['error'] else 'yellow')
        if start: self.root.variables.internalEvents['start'] = False
        if stop: self.root.variables.internalEvents['stop'] = False

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
        self.frame = Frame(master = root)
        self.frame.pack()
        self.Alive = True
        self.loop()

    def loop(self):
        while self.Alive:
            self.window.update()
            self.frame.update()
            self.window.variables.update()
            self.Alive = self.window.variables.Alive

if __name__ == '__main__':
    filepath = str(Path(__file__).parent.absolute())+'//widgetsettings.json'
    Window(object, filepath)
    