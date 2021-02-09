import tkinter as tk
from tkinter import ttk
from Variables import Variables

class SettingsScreen(tk.Frame):
    def __init__(self, master = None, variables = Variables()):
        super().__init__(master = master)
        self.variables = variables
        self.master = master
        self.name = 'Ustawienia i tryb ręczny'
        self.pack()
