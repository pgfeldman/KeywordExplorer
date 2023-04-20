import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Union

import keyword_explorer.tkUtils.ConsoleDprint as DP

class TopicComboExt():
    name:str
    tk_label:tk.Label
    tk_entry:tk.Entry
    tk_text:tk.Text
    tk_combo:ttk.Combobox
    wrapper:tk.Frame
    row:int = 0
    col:int = 0
    combo_str_var:tk.StringVar
    combo_vals:List
    parent:'tk.Frame'
    dp:DP.ConsoleDprint
    callback_fn:Callable
    callback_exists:bool
    default_behavior:bool
    use_text_field:bool

    def __init__(self, parent:'tk.Frame', row:int, label:str, dprint:DP.ConsoleDprint,
                 entry_width:int = 30, combo_width:int = 30, label_width:int=20, use_text_field:bool = False):
        self.parent = parent
        self.name = label
        self.set_dprint(dprint)
        self.row = row
        self.combo_str_var = tk.StringVar(value="Option 4")
        self.combo_vals = []
        self.tk_label = ttk.Label(parent, text=label, width=label_width)
        self.use_text_field = use_text_field
        self.callback_fn = None
        self.callback_exists = False

        self.wrapper = tk.Frame(parent)
        if self.use_text_field == True:
            self.tk_text = tk.Text(self.wrapper, width=entry_width, height=4, wrap=tk.WORD, borderwidth=2, relief="groove")
        else:
            self.tk_entry = ttk.Entry(self.wrapper, width=entry_width)
        self.tk_combo = ttk.Combobox(self.wrapper, values=self.combo_vals, width=combo_width)
        self.tk_combo.bind("<<ComboboxSelected>>", self.on_combobox_selected)

        self.tk_label.grid(column=0, row=row, sticky=(tk.W), padx=5)
        self.wrapper.grid(column=1, row=row, sticky=("nsew"))
        if use_text_field == True:
            self.tk_text.grid(column=1, row=0, sticky=(tk.N, tk.W), pady=2, padx=5)
        else:
            self.tk_entry.grid(column=1, row=0, sticky=(tk.N, tk.W), pady=2, padx=5)
        self.tk_combo.grid(column=2, row=0, sticky=(tk.N, tk.E), pady=2, padx=5)
        self.col = 3

    def add_button(self, name:str, command:Callable) -> ttk.Button:
        b = ttk.Button(self.wrapper, text=name, command=command)
        b.grid(column=self.col, row=0, sticky=(tk.N, tk.W), pady=2, padx=5)
        self.col += 1
        return b

    def set_label(self, s:str):
        self.tk_label.config(text = s)

    def set_callback(self, fn:Callable):
        self.callback_exists = True
        self.callback_fn = fn

    def set_dprint(self, con:DP.ConsoleDprint):
        self.dp = con

    def get_next_row(self):
        return self.row + 1

    def clear(self):
        if self.use_text_field:
            self.tk_text.delete('1.0', tk.END)
        else:
            self.tk_entry.delete(0, 'end')

    def set_text(self, text:str, pos:int = 0):
        if self.use_text_field:
            self.tk_text.delete('1.0', tk.END)
            self.tk_text.insert("1.0", text)
        else:
            self.tk_entry.insert(pos, text)

    def get_text(self) -> str:
        if self.use_text_field:
            return self.tk_text.get("1.0", tk.END)
        return self.tk_entry.get()

    def get_list(self) -> List:
        return self.combo_vals

    def set_combo_list(self, l:List):
        self.combo_vals = l.copy()
        self.tk_combo['values'] = self.combo_vals

    def add_to_combo_list(self, s:str):
        self.combo_vals.append(s)
        self.tk_combo.set(s)
        self.tk_combo['values'] = self.combo_vals

    def on_combobox_selected(self, event:tk.Event):
        if self.callback_exists:
            print("TopicComboExt.on_combobox_selected() name = {}".format(self.name))
            self.callback_fn(event)
        else:
            print("TopicCombo().on_combobox_selected: selected: {}".format(self.tk_combo.get()))
            self.clear()
            self.set_text(self.tk_combo.get())
