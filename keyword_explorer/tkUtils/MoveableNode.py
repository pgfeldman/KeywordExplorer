import math

import numpy as np
from tkinter import font
from enum import Enum

from keyword_explorer.tkUtils.ConsoleDprint import ConsoleDprint
from keyword_explorer.tkUtils.CanvasData import CanvasData

from typing import List, Dict, Union

class NODE_TYPE(Enum):
    MOVEABLE = 0
    FORCE = 1

class MovableNode:
    type:NODE_TYPE
    name:str
    cd:CanvasData
    dp = ConsoleDprint
    name:str
    id:int
    text_id:int
    size:float
    x:float
    y:float
    dx:float
    dy:float
    cx:float
    cy:float
    canvas_scalar:float
    canvas_x:float
    canvas_y:float
    target:Union['MovableNode', None]
    ty:float
    speed:float
    elapsed:float
    selected:bool
    show_name:bool
    selected_color = "red"
    size:float
    color:str
    neighbor_dict:Dict
    all_nodes_list:list

    def __init__(self, name:str, canvas:CanvasData, dprint:ConsoleDprint, color:str, size:float,
                 x:float, y:float, dx:float=0, dy:float=0, show_name:bool = True):
        self.type = NODE_TYPE.MOVEABLE
        self.name = name
        self.cd = canvas
        self.selected = False
        self.color = color
        self.size = size
        self.show_name = show_name
        # canvas transformations
        self.canvas_scalar = 1.0
        self.canvas_x = 0
        self.canvas_y = 0
        # position
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.cx = x+self.adjust_size(size)/2
        self.cy = y+self.adjust_size(size)/2
        # target position
        self.target = None
        self.elapsed = 1.0
        self.speed = 1.0
        self.neighbor_dict = {}
        self.set_dir_vec(dx, dy)
        self.set_dprint(dprint)
        self.font = font.Font(family='Helvetica', size=10)

        self.id = self.cd.canvas.create_oval(
            (self.x, self.y),
            (self.x + self.adjust_size(size), self.y + self.adjust_size(size)),
            fill=color)
        if self.show_name:
            self.text_id = self.cd.canvas.create_text(self.x, self.y, text=self.name, font=self.font)

    def set_dprint(self, con:ConsoleDprint):
        self.dp = con

    def to_string(self, prefix:str = "\n\t") -> str:
        s = "{}pos = ({:.3f}, {:.3f})".format(prefix, self.cx, self.cy)
        s += "{}size = {}".format(prefix, self.size)
        return s

    @staticmethod
    def adjust_size(size, scalar:float=5.0) -> float:
        return math.log2(size+1)*scalar

    def set_screen_coords(self):
        coords = self.cd.canvas.coords(self.id)
        self.cx = (coords[0] + coords[2])/2
        self.cy = (coords[1] + coords[3])/2

    def set_size(self, size:float):
        r = self.adjust_size(size)
        #r = min(r, 100)
        self.cd.canvas.coords(self.id, self.cx-r, self.cy-r, self.cx+r, self.cy+r)

    def reset_size(self):
        self.set_size(self.size/2)

    def set_canvas_offsets(self, s:float, x:float, y:float):
        self.canvas_x = x
        self.canvas_y = y
        self.canvas_scalar = s

    def set_dir_vec(self, dx:float, dy:float):
        self.dx = dx
        self.dy = dy
        v = np.array([dx, dy])
        d = np.sqrt(np.sum(v*v))
        if d != 0:
            nv = v/d
            self.dx = nv[0]
            self.dy = nv[1]

    def set_pos(self, x:float, y:float):
        self.x = x
        self.y = y

    def set_all_nodes_list(self, l:List):
        self.all_nodes_list = l

    def add_neighbor(self, n:'MovableNode', debug:bool = False):
        if n in self.neighbor_dict:
            if debug:
                print("MovableNode.add_neighbor(): skipping existing neighbor {}".format(n.name))
            return
        if debug:
            print("MovableNode.add_neighbor(): {} adding neighbor: {}".format(self.name, n.name))
        off1 = self.adjust_size(self.size)/2
        off2 = self.adjust_size(n.size)/2
        line_id = self.cd.canvas.create_line(self.x+off1, self.y+off1, n.x+off2, n.y+off2)
        self.cd.canvas.lower(line_id)
        self.neighbor_dict[n] = line_id

    def clear_neighbors(self):
        for name, id in self.neighbor_dict.items():
            self.cd.canvas.delete(id)
        self.neighbor_dict = {}

    def set_target(self, node:'MovableNode'):
        #print("setting target to {} ({}, {}".format(node.name, node.x, node.y))
        self.target = node

    def dist_to_target(self, dx, dy) -> float:
        v = np.array([dx, dy])
        d = np.sqrt(np.sum(v*v))
        return d

    # head towards target
    def step(self, elapsed:float = 0.1, scalar:float = 1.0):
        self.elapsed = elapsed

        factor = elapsed * scalar * self.speed
        if self.target != None:
            dx = self.target.cx - self.cx
            dy = self.target.cy - self.cy
            d = self.dist_to_target(dx, dy)

            if d > 0.0 and d * factor > self.adjust_size(self.size)/4 * factor:
                dx /= d
                dy /= d
                self.dx = dx * factor
                self.dy = dy * factor
                self.x += self.dx
                self.y += self.dy
                self.move(self.dx, self.dy)

        #print("{} = ({}, {}".format(self.name, self.x, self.y))
    def move(self, dx:float, dy:float):
        self.cd.canvas.move(self.id, dx, dy)
        if self.show_name:
            self.cd.canvas.move(self.text_id, dx, dy)
        self.set_screen_coords()

        for n, l in self.neighbor_dict.items():
            self.cd.canvas.coords(l, self.cx, self.cy, n.cx, n.cy)

    def set_color(self, color:str):
        self.cd.canvas.itemconfig(self.id, fill=color)

    def reset_color(self):
        self.cd.canvas.itemconfig(self.id, fill=self.color)

    def set_selected(self, state:bool):
        self.selected = state
        if state:
            self.set_color(self.selected_color)
        else:
            self.reset_color()

