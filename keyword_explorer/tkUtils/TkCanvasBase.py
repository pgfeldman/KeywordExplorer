from tkinter import *
from tkinter import ttk
from tkinter import font
import tkinter.font as tkf
import networkx as nx
import os
import textwrap
import random
from typing import List, Dict
from keyword_explorer.tkUtils.ListField import ListField
from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.tkUtils.DataField import DataField

class TkCanvasBase:
    root:Tk
    datafields:Dict
    mainframe:ttk.Frame
    left_frame:ttk.Frame
    right_frame:ttk.Frame
    bottom_frame:ttk.Frame
    main_console:TextField
    canvas:Canvas
    canvas_width:int
    canvas_height:int
    main_graphics = None
    current_dir:str
    dcount:int
    gml_model:nx.Graph
    node_list:List
    node_color = "lightblue"
    hover_color = "pink"
    select_color = "red"
    edge_color = "lightgrey"
    font:font

    def __init__(self, root:Tk, version:str):
        self.reset()
        self.root = root
        self.root.title("TkCanvasBase {}".format(version))
        self.mainframe = ttk.Frame(self.root, borderwidth=2, relief="groove")
        self.mainframe.grid(column=0, row=0, sticky=(N,W,E,S))

        self.build_menus()
        self.build_left()
        self.build_right()
        self.build_bottom()
        self.set_resize()
        self.current_dir = os.getcwd()
        self.dprint("Current dir = {}".format(self.current_dir))

        self.dprint(version)

    def reset(self):
        print("TkCanvasBase.reset()")
        self.root:Tk = None
        self.font = font.Font(family='Helvetica', size=12)
        self.mainframe = None
        self.main_console = None
        self.main_graphics = None
        self.canvas = None
        self.canvas_width = 600
        self.canvas_height = 500
        self.current_dir = None
        self.datafields = {}
        self.dcount = 0
        self.gml_model = None
        self.node_list = []
        for i in range(10):
            self.node_list.append("node_{:02}".format(i))

    def build_menus(self):
        print("building menus")
        self.root.option_add('*tearOff', FALSE)
        menubar = Menu(self.root)
        self.root['menu'] = menubar
        self.add_menus(menubar)


    def add_menus(self, menubar:Menu):
        menu_file = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Exit', command=self.terminate)

    def build_left(self):
        self.left_frame = ttk.Frame(self.mainframe,  borderwidth=5, relief="groove")
        self.left_frame.grid(column=0, row=0, sticky=(N,W,E,S))
        row = 0
        row = self.add_left_components(self.left_frame, row)
        row += 1
        row = self.create_textfield("console", self.left_frame, row, "Console", "", 30, 10)
        self.main_console = self.datafields["console"]

    def add_left_components(self, f:ttk.Frame, row:int) -> int:
        return row

    def build_right(self):
        self.right_frame = ttk.Frame(self.mainframe,  borderwidth=5, relief="groove")
        self.right_frame.grid(column=1, row=0, sticky=(N,W,E,S))
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)
        self.canvas = Canvas(self.right_frame, bg="white", height=self.canvas_height, width=self.canvas_width)
        self.canvas.bind("<Button-1>", self.canvas_event_callback)
        self.canvas.pack(fill="both", expand=True)

        for n in self.node_list:
            size = random.randint(10, 50)
            x0 = random.randint(20, 500)
            y0 = random.randint(20, 500)
            x1 = x0+size
            y1 = y0+size
            self.canvas.create_oval(x0, y0, x1, y1, fill=self.node_color, activefill=self.hover_color, tags=n)
            self.canvas.create_text(x0, y0, text=n, font=self.font)


        self.gml_model = nx.Graph(name="default")
        for n in self.node_list:
            self.gml_model.add_node(n, graphics={"fill":"lightblue"})


        num_edges = 2
        for n1 in self.node_list:
            for i in range(num_edges):
                n2 = random.choice(self.node_list)
                if n1 != n2:
                    self.gml_model.add_edge(n1, n2)
                    sx, sy, tx, ty = self.get_line_coords(n1, n2)
                    id = self.canvas.create_line(sx, sy, tx, ty, fill=self.edge_color)
                    self.canvas.lower(id)

    def canvas_event_callback(self, event:Event):
        self.dprint("clicked at ({}, {})".format(event.x, event.y))
        self.canvas_callback_actions(event)

    def canvas_callback_actions(self, event:Event):
        pass

    def build_bottom(self):
        self.bottom_frame = ttk.Frame(self.mainframe,  borderwidth=5, relief="groove")
        self.bottom_frame.grid(column=0, row=1, columnspan=2, sticky=(N,W,E,S))
        #self.bottom_frame.columnconfigure(1, weight=1)
        self.bottom_frame.rowconfigure(0, weight=1)
        row = 0
        row = self.create_textfield("path", self.bottom_frame, row, "Path", "", 110, 10)

    def get_center(self, n:str) -> [int, int]:
        c = self.canvas.coords(n)
        bb = self.canvas.bbox(n)
        x = c[0] + (bb[2] - bb[0])/2
        y = c[1] + (bb[3] - bb[1])/2
        return (int(x), int(y))


    def get_line_coords(self, n1:str, n2:str) -> [int, int, int, int]:
        sx, sy = self.get_center(n1)
        tx, ty = self.get_center(n2)
        return (sx, sy, tx, ty)

    def create_datafield(self, name:str, parent:'ttk.Frame', row:int, label:str, default:str, width:int = 20) -> int:
        df = DataField(parent, row, label, width)
        df.set_text(default)
        self.datafields[name] = df
        return df.get_next_row()

    def create_textfield(self, name:str, parent:'ttk.Frame', row:int, label:str, default:str, width:int = 20, height:int = 3) -> int:
        tf = TextField(parent, row, label, width=width, height=height)
        tf.add_text(default)
        self.datafields[name] = tf
        return tf.get_next_row()

    def create_listfield(self, name:str, parent:'ttk.Frame', row:int, label:str, default:str, width:int = 20, height:int = 3, selectmode=MULTIPLE) -> int:
        lf = ListField(parent, row, label, width=width, height=height, selectmode=selectmode)

        lf.set_text(default)
        self.datafields[name] = lf
        return lf.get_next_row()

    def set_resize(self):
        print("adding resizing")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=0)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)


    def log_path(self, d:Dict, clear:bool = True):
        tf:TextField = self.datafields["path"]
        if clear:
            tf.tk_text.delete('1.0', END)
        tf.tk_text.insert(END, "path = {}".format(d.keys()))
        for key, val in d.items():
            line = "{}: {}\n".format(key, val)
            tf.tk_text.insert(END, line)

    def dprint(self, text: str, max_chars:int = -1):
        if self.main_console:
            if max_chars > -1:
                text = textwrap.shorten(text, width=max_chars)

            self.main_console.tk_text.insert("1.0", "[{}] {}\n".format(self.dcount, text))
            # self.main_console.set_text(text, self.dcount)
            self.dcount += 1
            self.mainframe.update()
        else:
            print(text)

    def terminate(self):
        print("terminating")
        self.root.destroy()

    def impliment_me(self):
        self.dprint("Implement me!")



def main():
    root = Tk()
    print(tkf.families())
    tcb = TkCanvasBase(root, "Version 0.1")
    root.mainloop()

if __name__ == "__main__":
    main()