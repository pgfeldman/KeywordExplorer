import tkinter as tk
from tkinter import ttk
import random
import re
from typing import List, Callable


class TextField:
    name = "unset"
    value = None
    tk_label:ttk.Label
    tk_text:tk.Text
    lvar:tk.StringVar = None
    row = 0
    reference_text:str
    animate_index:int
    animate_delay_ms:int
    select_callback:Callable
    modified_callback:Callable

    def __init__(self, parent:'ttk.Frame', row:int, label:str, width:int = 20, height: int = 3, label_width:int=20):
        self.row = row
        self.lvar = tk.StringVar(value=label)
        self.tk_label = ttk.Label(parent, textvariable=self.lvar, width=label_width)
        text_wrapper = tk.Frame(parent, borderwidth=2)
        self.tk_text = tk.Text(text_wrapper, width=width, height=height, wrap=tk.WORD, borderwidth=2, relief="groove")
        #self.tk_text.bind('<<Selection>>', self.on_text_select)
        #self.tk_text.bindtags(('Text', '.tk_text', '.', 'all'))
        #self.tk_text.bind("<Key>", self.on_text_modified)
        #self.tk_text.bind_class('post-class-bindings', '<Key>', self.on_text_modified)

        text_scrollbar = ttk.Scrollbar(text_wrapper, orient=tk.VERTICAL, command=self.tk_text.yview)
        self.tk_text['yscrollcommand'] = text_scrollbar.set


        self.tk_label.grid(column=0, row=row, sticky=(tk.W), padx=5)
        text_wrapper.grid(column=1, row=row, rowspan=height, sticky=(tk.N, tk.S, tk.E, tk.W), pady=2, padx=5)
        self.tk_text.grid(column=0, row=0, rowspan=1, sticky=(tk.N, tk.S, tk.E, tk.W), pady=0, padx=0)
        text_scrollbar.grid(column=1, row=0, rowspan=1, sticky=(tk.N, tk.S))

        parent.columnconfigure(1, weight=1)
        text_wrapper.columnconfigure(0, weight=1)

        self.row = row + height
        self.select_callback = None
        self.modified_callback = None

    def set_label(self, label:str):
        self.lvar.set(label)

    def set_select_callback(self, fn:Callable):
        self.select_callback = fn

    def set_modified_callback(self, fn:Callable):
        self.modified_callback = fn

    def get_next_row(self):
        return self.row + 1

    def clear(self):
        self.tk_text.delete('1.0', tk.END)

    def set_text(self, text:str, pos:int = 0):
        self.reference_text = text
        self.tk_text.delete('1.0', tk.END)
        self.tk_text.insert("1.0", text)

    def set_animate_text(self, text:str, animate_delay:int = 30):
        self.reference_text = text
        self.animate_delay_ms = animate_delay
        self.animate_index = 0
        self.tk_text.delete('1.0', tk.END)
        self.animate()

    def animate(self):
        if self.animate_index < len(self.reference_text):

            # print(self.animate_text[:self.animate_index])
            # self.tk_text.delete('1.0', tk.END)
            # self.tk_text.insert("1.0", self.animate_text[:self.animate_index])
            self.tk_text.insert(tk.END, self.reference_text[self.animate_index])
            self.animate_index += 1
            delay = abs(self.animate_delay_ms)
            if self.animate_delay_ms < 0:
                delay += random.randint(0, delay*5)
            self.tk_text.after(delay, self.animate)

    def add_text(self, text:str, pos:int = 0):
        self.tk_text.insert("1.0", text)

    def get_text(self) -> str:
        to_return = self.tk_text.get("1.0", tk.END).strip()
        return to_return

    def get_reference_text(self) -> str:
        return self.reference_text

    def get_list(self, regex_str:str = ",") -> List:
        to_return = self.tk_text.get("1.0", tk.END)
        rlist = re.split(regex_str, to_return)
        to_return = []
        for t in rlist:
            to_return.append(t.strip())
        to_return = [x for x in to_return if x] # filter out the blanks
        return to_return

    def get_selected(self, get_everything:bool = True) -> str:
        # if nothing is selected, the we'll grab everything. We take advantage of the exception that is thrown when
        # you try to get the index of a selection that is not there
        s = ""
        try:
            start = self.tk_text.count('1.0', tk.SEL_FIRST)
            s = self.tk_text.selection_get()
        except tk.TclError:
            if get_everything:
                s = self.get_text()
        #print("selected {}\n".format(s))
        return s

    def on_text_select(self, event:tk.Event):
        try:
            if self.select_callback != None:
                s = self.tk_text.selection_get()
                self.select_callback(s)
        except tk.TclError:
            pass

    def on_text_modified(self, event:tk.Event):

        try:
            if self.modified_callback != None:
                s = self.get_text()
                #print("s = {}".format(s))
                self.modified_callback(s)
        except tk.TclError:
            pass

