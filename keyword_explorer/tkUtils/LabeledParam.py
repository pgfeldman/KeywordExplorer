import tkinter as tk
from tkinter import ttk
from typing import List, Any, Callable

class LabeledParam:
    tk_label = None
    tk_entry = None

    def __init__(self, parent:'ttk.Frame', col:int, label:str, label_width:int = 0, entry_width = 5, sticky="nsew"):

        self.tk_label = tk.Label(parent, text=label, width=len(label)+label_width, anchor="w")#, background="pink")
        self.tk_entry = tk.Entry(parent, width=entry_width)
        self.tk_label.grid(column=col, row=0, sticky=sticky, padx=2)
        self.tk_entry.grid(column=col+1, row=0, sticky=sticky, pady=2, padx=5)

    def tuple_extract(self, obj:Any, index:int=0) -> Any:
        if isinstance(obj, tuple):
            return obj[index]
        return obj

    def clear(self):
        self.tk_entry.delete(0, 'end')

    def set_bg_color(self, color:str="white"):
        print("set_bg_color: {}".format(color))
        self.tk_entry.configure(background = color)

    def set_text(self, text:str, pos:int = 0):
        self.tk_entry.delete(0, 'end')
        self.tk_entry.insert(pos, text)

    def get_text(self) -> str:
        return self.tuple_extract(self.tk_entry.get())

    def get_as_int(self, base:int = 10) -> any:
        try:
            return int(self.tuple_extract(self.get_text()), base)
        except:
            return self.get_text()

    def get_as_float(self) -> any:
        try:
            return float(self.get_text())
        except:
            return self.get_text()


    def get_list(self) -> List:
        to_return = self.tk_entry.get()
        rlist = to_return.split(',')
        to_return = []
        for t in rlist:
            to_return.append(t.strip())
        to_return = [x for x in to_return if x] # filter out the blanks
        return to_return