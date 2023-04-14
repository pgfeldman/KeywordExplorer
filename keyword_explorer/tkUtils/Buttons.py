import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Any

class Buttons():
    tk_label:tk.Label
    tk_combo:ttk.Combobox
    tk_button:ttk.Button
    wrapper:tk.Frame
    row = 0
    col:int = 0
    parent:'tk.Frame'
    label_dict:Dict

    def __init__(self, parent:'tk.Frame', row:int, label:str, label_width:int=20, sticky="nsew"):
        self.label_dict = {}
        self.parent = parent
        self.row = row
        self.tk_label = tk.Label(parent, text=label, width=label_width, anchor="w")#, background="pink")
        self.tk_label.grid(column=0, row=row, sticky="w", padx=5)

        self.wrapper = tk.Frame(parent)#, background="pink")
        self.wrapper.grid(column=1, row=row, sticky=sticky)

        self.col = 0

    def add_button(self, name:str,  command:Callable, width:int = 10, sticky:Any = (tk.N, tk.W)) -> ttk.Button:
        if width < 0:
            width = len(name)+1
        sv = tk.StringVar()
        sv.set(name)
        b = ttk.Button(self.wrapper, textvariable=sv, width=width, command=command)
        b.grid(column=self.col, row=0, sticky=sticky, pady=2, padx=5)
        self.col += 1
        self.label_dict[name] = sv
        return b

    def change_button_label(self, name:str, label:str):
        sv:tk.StringVar = self.label_dict[name]
        sv.set(label)

    def get_button_label(self, name:str) -> str:
        sv:tk.StringVar = self.label_dict[name]
        return sv.get()

    def get_label_dict(self) -> Dict:
        return self.label_dict

    def get_next_row(self):
        return self.row + 1

