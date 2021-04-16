import tkinter as tk
from tkinter import ttk
from .common import LabelFrame, GeneralWidget, KEYWORDS, Lamp

class StatusIndicators(LabelFrame):
    def __init__(self, master = None, branch = 'StatusIndicators'):
        super().__init__(master = master, branch = branch)
        for key in self.settings.keys():
            if key in KEYWORDS: continue
            indicator = Lamp(self, branch = key)
            indicator.pack()

