import tkinter as tk
from tkinter import ttk
from Home import HomeScreen
from Settings import SettingsScreen
from Table import TableScreen
from Variables import Variables
from Widgets.ScrolledText import LabelledScrolledText

class Frame(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.OverallNotebook = ttk.Notebook(self)
        self.widgets = [
            LabelledScrolledText(master = self, variables = self.variables, InternalVariable= 'ImportantMessages', scrolltype='vertical', height=5, text = 'Błędy i powiadomienia'),
            HomeScreen(master = self.OverallNotebook, variables = self.variables),
            SettingsScreen(master = self.OverallNotebook, variables = self.variables),
            TableScreen(master = self.OverallNotebook, variables = self.variables) ]
        for widget in self.widgets:
            if hasattr(widget, 'name'):
                self.OverallNotebook.add(widget, text=widget.name)
            else:
                widget.pack(side = tk.BOTTOM, expand = tk.NO, fill = tk.X)
        self.OverallNotebook.pack(side = tk.LEFT, expand = tk.YES, fill=tk.BOTH)

    def update(self):
        super().update()
        for widget in self.widgets:
            widget.update()

class Window():
    def __init__(self, lockerinstance):
        self.window = tk.Tk()
        self.variables = Variables()
        self.window.title('Spawanie Lusterkowe VG')
        self.window.attributes('-fullscreen', True)
        self.master = tk.Frame(self.window)
        self.widgets = [
            Frame(master = self.master, variables = self.variables) ]
        for widget in self.widgets:
            widget.pack(side = tk.LEFT, expand = tk.Y, fill='both')
        self.master.pack(side = tk.LEFT, expand = tk.Y, fill='both')
        self.Alive = True
        self.loop()

    def loop(self):
        while self.Alive:
            self.window.update()
            for widget in self.widgets:
                widget.update()

if __name__ == '__main__':
    Window(object)