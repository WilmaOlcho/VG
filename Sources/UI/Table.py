import tkinter as tk
from tkinter import ttk

class TableScreen(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master = master)
        self.master = master
        self.name = 'Table'
        self.pack()
