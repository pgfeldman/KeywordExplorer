import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Union

import keyword_explorer.tkUtils.ConsoleDprint as DP

class TopicCombo():
    tk_label:tk.Label
    tk_combo:ttk.Combobox
    tk_button:ttk.Button
    wrapper:tk.Frame
    row = 0
    col:int = 0
    combo_str_var:tk.StringVar
    button_str_var:tk.StringVar
    combo_vals:List
    combo_width:int
    parent:'tk.Frame'
    dp:DP.ConsoleDprint
    combo_callback_fn:Union[Callable, None]
    button_callback_fn:Union[Callable, None]
    last_selected:str = None

    def __init__(self, parent:'tk.Frame', row:int, label:str, dprint:DP.ConsoleDprint = None,
                 button_label:str = "Set Group", combo_width:int = 30, label_width:int=20):
        self.parent = parent
        self.set_dprint(dprint)
        self.row = row
        self.combo_width = combo_width
        self.combo_str_var = tk.StringVar(value="Option 4")
        self.combo_vals = []
        self.tk_label = ttk.Label(parent, text=label, width=label_width)
        self.combo_callback_fn = None
        self.button_callback_fn = None

        self.wrapper = tk.Frame(parent)
        self.tk_combo = ttk.Combobox(self.wrapper, values=self.combo_vals, width=combo_width)
        self.tk_combo.bind("<<ComboboxSelected>>", self.on_combobox_selected)
        self.tk_combo['state'] = 'readonly'

        self.button_str_var = tk.StringVar()
        self.set_button_text(button_label)
        self.tk_button = ttk.Button(self.wrapper, textvariable=self.button_str_var, command=self.on_button_clicked)

        self.tk_label.grid(column=0, row=row, sticky=(tk.W), padx=5)
        self.wrapper.grid(column=1, row=row, sticky=("nsew"))
        self.tk_combo.grid(column=0, row=0, sticky=(tk.N, tk.W), pady=2, padx=5)
        self.tk_button.grid(column=1, row=0, sticky=(tk.N, tk.W), pady=2, padx=5)
        self.col = 2

    def add_button(self, name:str, command:Callable) -> ttk.Button:
        b = ttk.Button(self.wrapper, text=name, command=command)
        b.grid(column=self.col, row=0, sticky=(tk.N, tk.W), pady=2, padx=5)
        self.col += 1
        return b

    def set_combo_callback(self, fn:Callable):
        self.combo_callback_fn = fn

    def set_button_callback(self, fn:Callable):
        self.button_callback_fn = fn

    def set_dprint(self, con:DP.ConsoleDprint):
        self.dp = con

    def set_button_text(self, s:str):
        self.button_str_var.set(s)

    def enable_button(self, state:bool):
        if state:
            self.tk_button['state'] = 'normal'
        else:
            self.tk_button['state'] = 'disabled'

    def get_next_row(self):
        return self.row + 1

    def get_list(self) -> List:
        return self.combo_vals

    def set_combo_list(self, l:List):
        self.combo_vals = l.copy()
        self.tk_combo['values'] = self.combo_vals
        if self.last_selected in self.combo_vals:
            self.tk_combo.set(self.last_selected)

    def add_to_combo_list(self, s:str):
        if len(s) > self.combo_width:
            s = "{}...".format(s[:self.combo_width])
        self.combo_vals.append(s)
        self.tk_combo.set(s)
        self.tk_combo['values'] = self.combo_vals
        if self.last_selected in self.combo_vals:
            self.tk_combo.set(self.last_selected)

    def clear_combo(self):
        self.combo_vals = []
        self.tk_combo['values'] = self.combo_vals

    def set_combo_index(self, index:int = 0):
        self.tk_combo.current(index)
        self.last_selected = self.tk_combo.get()

    def on_combobox_selected(self, event:tk.Event):
        self.last_selected = self.tk_combo.get()
        if self.combo_callback_fn != None:
            self.combo_callback_fn(event)
        else:
            print("TopicCombo().on_combobox_selected: selected: {}".format(self.tk_combo.get()))

    def on_button_clicked(self):
        if self.button_callback_fn != None:
            self.button_callback_fn()
        else:
            print("TopicCombo().button_callback_fn: clicked")
