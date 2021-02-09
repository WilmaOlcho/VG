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
            LabelledScrolledText(master = self, variables = self.variables, InternalVariable= 'ImportantMessages', scrolltype='vertical', height=5, width = 200, text = 'Błędy i powiadomienia'),
            tk.Button(master = self, text = 'Potwierdź\nstatus', command = self.ack, bg = 'yellow', width = 14, height = 6),
            HomeScreen(master = self.OverallNotebook, variables = self.variables),
            SettingsScreen(master = self.OverallNotebook, variables = self.variables),
            TableScreen(master = self.OverallNotebook, variables = self.variables) ]
        col = 0
        for widget in self.widgets:
            if hasattr(widget, 'name'):
                self.OverallNotebook.add(widget, text=widget.name)
            else:
                widget.grid(column = col, row=0)
                col +=1
        self.OverallNotebook.grid(columnspan = col-1, row = 1)

    def update(self):
        super().update()
        for widget in self.widgets:
            if isinstance(widget, tk.Button):
                widget.config(bg = 'red' if self.variables.internalEvents['error'] else 'yellow')
            widget.update()

    def ack(self):
        self.variables.internalEvents['ack'] = True

class Window():
    def __init__(self, lockerinstance):
        self.window = tk.Tk()
        self.variables = Variables()
        self.window.title('Spawanie Lusterkowe VG')
        self.window.attributes('-fullscreen', True)
        self.master = tk.Frame(self.window)
        self.interfaceControl = InterfaceControl(lockerinstance, self.variables)
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
            self.interfaceControl.update()

class InterfaceControl(object):
    def __init__(self, lockerinstance, variables = Variables()):
        self.variables = variables
        pass

    def update(self):
        if self.variables.internalEvents['ack']:
            self.variables.internalEvents['error'] = False
            self.variables.internalEvents['ack'] = False

if __name__ == '__main__':
    Window(object)
