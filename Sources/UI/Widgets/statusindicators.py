import tkinter as tk
from tkinter import ttk
from .common import LabelFrame, GeneralWidget, KEYWORDS

class StatusIndicators(LabelFrame):
    def __init__(self, master = None):
        super().__init__(master = master, branch = 'StatusIndicators')
        for key, indicator in self.settings.items():
            if key in KEYWORDS: continue
            self.widgets.append(StatusIndicators.line(self, label = indicator['Label'], indicator = key))
        for widget in self.widgets:
            widget.pack()
        self.pack()

    class line(GeneralWidget):
        def __init__(self, master = None, label = '', indicator = ''):
            super().__init__(master = master, branch = indicator)
            self.key = indicator
            self.config(**self.settings['Frame'])
            self.cwidth = self.settings['Frame']['height']
            self.place = self.cwidth//2
            self.__setattr__('settings', self.settings)
            self.label = ttk.Label(self)
            self.label.config(text=label)
            self.label.place(anchor='w', x='3', y=self.place)
            self.indicator = tk.Canvas(self)
            self.indicator.config(background='Black', height=self.cwidth, width=self.cwidth, bd = 0)
            self.indicator.place(anchor='e', x=self.settings['Frame']['width'], y=self.place)
        
        def update(self):
            self.indicator.config(bg = 'lightgreen' if self.root.variables.statusindicators[self.key]==1 else 'black' if self.root.variables.statusindicators[self.key]==0 else 'red' if self.root.variables.statusindicators[self.key]==-1 else 'blue')
            super().update()
