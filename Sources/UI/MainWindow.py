import tkinter as tk
from tkinter import ttk
from Home import HomeScreen
from Settings import SettingsScreen
from Table import TableScreen
from Variables import Variables

class Frame(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.OverallNotebook = ttk.Notebook(self)
        self.widgets = [
            HomeScreen(master = self.OverallNotebook, variables = self.variables),
            SettingsScreen(master = self.OverallNotebook, variables = self.variables),
            TableScreen(master = self.OverallNotebook, variables = self.variables) ]
        for widget in self.widgets:
            self.OverallNotebook.add(widget, text=widget.name)
        self.OverallNotebook.pack(side = tk.LEFT, expand = tk.Y, fill='both')

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