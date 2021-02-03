import tkinter as tk
from tkinter import ttk
from Home import HomeScreen
from Settings import SettingsScreen
from Table import TableScreen


class Frame(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master = master)
        self.OverallNotebook = ttk.Notebook(self)
        self.widgets = [
            HomeScreen(master = self.OverallNotebook),
            SettingsScreen(master = self.OverallNotebook),
            TableScreen(master = self.OverallNotebook) ]
        for widget in self.widgets:
            self.OverallNotebook.add(widget, text=widget.name)
        self.OverallNotebook.pack()

class Window():
    def __init__(self, lockerinstance):
        self.window = tk.Tk()
        self.window.title('Spawanie Lusterkowe VG')
        self.window.attributes('-fullscreen', True)
        self.master = tk.Frame(self.window)
        self.widgets = [
            Frame(master = self.master) ]
        for widget in self.widgets:
            widget.pack(side = tk.LEFT, expand = tk.Y, fill='both')
        self.master.pack(side = tk.LEFT, expand = tk.Y, fill='both')
        self.Alive = True
        self.window.mainloop()

    def loop(self):
        while self.Alive:
            self.window.update()

if __name__ == '__main__':
    Window(object)