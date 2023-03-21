import tkinter as tk
from tkinter import ttk
from keyword_explorer.tkUtils.Checkboxes import Checkbox
from typing import List, Any, Callable

class SelectParam:
    cb:Checkbox

    def __init__(self, parent:'ttk.Frame', col:int, label:str, command:Callable = None, label_width:int = 0, sticky="nsew", type = tk.CHECKBUTTON):
        self.cb = Checkbox(parent, name=label, command=command)
        self.cb.cb.grid(column=col+1, row=0, sticky=sticky, pady=2, padx=5)

    def get_value(self) -> bool:
        return self.cb.get_val()

    def set_value(self, val:bool):
        self.cb.set_val(val)