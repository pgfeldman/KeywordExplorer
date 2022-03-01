import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import List, Any

class DateEntryField:
    name = "unset"
    value = None
    tk_label = None
    tk_entry = None
    row = 0

    def __init__(self, parent:'ttk.Frame', row:int, label:str, width:int = 20, label_width:int = 20):
        self.row = row
        self.tk_label = ttk.Label(parent, text=label, width=label_width)
        self.tk_entry = tk.Entry(parent, width=width)

        self.tk_label.grid(column=0, row=row, sticky=(tk.W), padx=5)
        self.tk_entry.grid(column=1, row=row, sticky=(tk.N, tk.E, tk.W), pady=5, padx=5)

    def get_next_row(self):
        return self.row + 1

    def clear(self):
        self.tk_entry.delete(0, 'end')

    def set_bg_color(self, color:str="white"):
        print("set_bg_color: {}".format(color))
        self.tk_entry.configure(background = color)

    def set_date(self, d:datetime=None, pos:int = 0):
        self.tk_entry.delete(0, 'end')
        if d == None:
        # The most recent end time has to be ten seconds ago. To be on the safe side, we subtract one minute
            d = datetime.utcnow() - timedelta(minutes=1)
        text = d.strftime('%B %d, %Y')
        self.tk_entry.insert(pos, text)

    def get_text(self) -> str:
        return self.tk_entry.get()

    def get_date(self) -> datetime:
        s = self.tk_entry.get()
        d = datetime.strptime(s, "%B %d, %Y")
        return d
