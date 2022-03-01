import tkinter as tk
from tkinter import ttk
from typing import Union, List, Callable



class ListField:
    name:str = "unset"
    tk_labelttk:tk.Label = None
    tk_list:tk.Listbox = None
    row = 0
    term_list = ["call", "me", "Ishmael"]
    tvar:tk.StringVar = None
    lvar:tk.StringVar = None
    callback_fn:Callable = None
    callback_fn2:Callable = None
    sel_list:List
    last_selected:str = None
    static_list:bool = False

    def __init__(self, parent:'ttk.Frame', row:int, label:str, width:int = 20, height: int = 3, selectmode=tk.BROWSE, label_width:int=20, static_list:bool = False):
        self.static_list = static_list
        self.callback_fn = None
        self.sel_list = []
        self.last_selected = 'unset'
        self.tvar = tk.StringVar(value=self.term_list)
        self.lvar = tk.StringVar(value=label)
        self.row = row
        self.tk_label = ttk.Label(parent, textvariable=self.lvar, width=label_width)
        list_wrapper = tk.Frame(parent, borderwidth=2)
        self.tk_list = tk.Listbox(list_wrapper, listvariable=self.tvar, width=width, height=height, selectmode=selectmode)
        self.tk_list.bind('<<ListboxSelect>>', self.on_selected)
            #Text(text_wrapper, width=width, height=height, wrap=WORD, borderwidth=2, relief="groove")

        text_scrollbar = ttk.Scrollbar(list_wrapper, orient=tk.VERTICAL, command=self.tk_list.yview)
        self.tk_list['yscrollcommand'] = text_scrollbar.set


        self.tk_label.grid(column=0, row=row, sticky=(tk.W), padx=5)
        list_wrapper.grid(column=1, row=row, rowspan=height, sticky=(tk.N, tk.E, tk.W), pady=2, padx=5)
        self.tk_list.grid(column=0, row=0, rowspan=1, sticky=(tk.N, tk.S, tk.E, tk.W), pady=0, padx=0)
        text_scrollbar.grid(column=1, row=0, rowspan=1, sticky=(tk.N, tk.S))

        parent.columnconfigure(1, weight=1)
        list_wrapper.columnconfigure(0, weight=1)

        self.row = row + height

    def set_label(self, label:str):
        self.lvar.set(label)

    def get_next_row(self):
        return self.row + 1

    def clear(self):
        self.term_list = []
        self.tvar.set(self.term_list)

    def add_entry(self, s:str):
        self.term_list.append(s)
        self.tvar.set(self.term_list)

    def set_text(self, text:str = None, list:List = None, pos:int = 0, sort:bool = False):
        self.term_list = []
        if text:
            text = text.replace(" ", "")
            term_list = text.split(',')
            for t in term_list:
                t = t.strip()
                if t not in self.term_list:
                    self.term_list.append(t)
            if sort:
                self.term_list = sorted(self.term_list)
                self.term_list = [x for x in self.term_list if x]
            self.tvar.set(self.term_list)
        elif list:
            for t in list:
                t = t.strip()
                if t not in self.term_list:
                    self.term_list.append(t)
            if sort:
                self.term_list = sorted(self.term_list)
                self.term_list = [x for x in self.term_list if x] # filter out the blanks
            self.tvar.set(self.term_list)

        self.tk_list.select_set(0)
        self.last_selected = self.term_list[0]
        # Colorize alternating lines of the listbox
        for i in range(0,len(self.term_list),2):
            self.tk_list.itemconfigure(i, background='#f0f0ff')

    def get_text(self) -> str:
        to_return = self.term_list.join(",")
        return to_return

    def get_list(self) -> List:
        return self.term_list

    def get_next(self) -> str:
        return self.term_list[0]

    def get_selected(self) -> str:
        sel_list =  self.tk_list.curselection()
        s:str
        if len(sel_list) > 0:
            # find the first element in the list. It should be the only one
            for index in sel_list:
                self.last_selected = self.tk_list.get(index)
                break
        return self.last_selected

    def set_callback(self, fn:Callable):
        self.callback_fn = fn

    def on_selected(self, event:tk.Event):
        if not self.static_list:
            sel_list =  self.tk_list.curselection()
            if len(sel_list) > 0:
                for index in sel_list:
                    self.last_selected = self.tk_list.get(index)
                    # print("clicked on item[{}] = [{}]".format(index, s))
                    if index in self.sel_list:
                        self.tk_list.selection_clear(0, tk.END)
            self.sel_list = sel_list

        if self.callback_fn != None:
            self.callback_fn(event)
