import json
import tkinter as tk
import tkinter.ttk as ttk
from .common import LabelFrame, GeneralWidget, getroot

class ScrolledText(GeneralWidget, ttk.Frame):
    def __init__(self, master = None, InternalVariable = None, scrolltype = 'both', height=200, width=200):
        GeneralWidget.__init__(self, master)
        ttk.Frame.__init__(self, master = master, width = width, height = height)
        self.key = InternalVariable
        self.textInstance = tk.Text(self, height=height, width=width, font = self.root.font())
        if scrolltype in ('vertical','both'):
            self.vsb = tk.Scrollbar(self, orient='vertical', command = self.textInstance.yview)#, yscrollcommand = lambda f, l, obj = self:obj.autoscroll(self.vsb, f, l))
            self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        else: self.vsb = None
        if scrolltype in ('horizontal','both'):
            self.hsb = tk.Scrollbar(self, orient='horizontal', command = self.textInstance.xview)#, xscrollcommand = lambda f, l, obj = self:obj.autoscroll(self.hsb, f, l))
            self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        else: self.Hsb = None
        self.textInstance.configure(yscrollcommand=self.vsb.set if hasattr(self,'vsb') else None, xscrollcommand=self.hsb.set if hasattr(self,'hsb') else None)
        self.textInstance.pack(fill=tk.BOTH)
        self.vtext = ''

    def update(self):
        text = self.root.variables[self.key]
        if self.vtext != text:
            vpos, hpos = self.vsb.get() if hasattr(self,'vsb') else [0,0], self.hsb.get() if hasattr(self,'hsb') else [0,0]
            prevw, prevh = self.textInstance.winfo_width(), self.textInstance.winfo_height()
            self.textInstance.delete('1.0',tk.END)
            self.textInstance.insert('1.0',text)
            wsub = prevw/self.textInstance.winfo_width()
            hsub = prevh/self.textInstance.winfo_height()
            self.textInstance.xview_moveto(hpos[0]*wsub)
            self.textInstance.yview_moveto(vpos[0]*hsub)
            self.vtext = text

class LabelledScrolledText(GeneralWidget, ttk.LabelFrame):
    def __init__(self, master = None, text = '', InternalVariable = None, scrolltype = 'both', height=200, width=200):
        GeneralWidget.__init__(self, master)
        ttk.LabelFrame.__init__(self, master = master, text = text)
        self.text = ScrolledText(master = self, InternalVariable = InternalVariable, scrolltype = scrolltype, height=height, width=width)
        self.text.pack()
