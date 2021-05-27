import tkinter as tk
from tkinter import ttk
from .common import LabelFrame, GeneralWidget, KEYWORDS, Lamp, Entry
CLASSNAMES = ['LabelFrame', 'GeneralWidget', 'Lamp', 'Entry']
class StatusIndicators(LabelFrame):
    def __init__(self, master = None, branch = 'StatusIndicators'):
        super().__init__(master = master, branch = branch)
        for key in self.settings.keys():
            if key in KEYWORDS or key in CLASSNAMES:
                self.checkkeywords(key)
                continue
            indicator = Lamp(self, branch = key)
            indicator.pack()

    def checkkeywords(self, keyword):
        if keyword in CLASSNAMES:
            _class = eval(keyword)
            element = _class(master = self, branch = keyword)
            element.pack()
