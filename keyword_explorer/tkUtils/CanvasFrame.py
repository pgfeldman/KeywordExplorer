import tkinter as tk
from tkinter import ttk
import random
import math

from keyword_explorer.tkUtils.ConsoleDprint import ConsoleDprint
from keyword_explorer.tkUtils.CanvasData import CanvasData
from keyword_explorer.tkUtils.MoveableNode import MovableNode, NODE_TYPE
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.utils.SharedObjects import SharedObjects

from typing import List, Union, Callable


class CanvasMouse():
    canvas:tk.Canvas
    x:int
    y:int
    old_x:int
    old_y:int
    wheel:int
    b1_down:bool
    b1_dx:int
    b1_dy:int

    def __init__(self, canvas:tk.Canvas):
        print("CanvasMouse")
        self.canvas = canvas
        self.x = 0
        self.y = 0
        self.old_x = 0
        self.old_y = 0
        self.wheel = 0
        self.b1_down = False
        self.b1_dx = 0
        self.b1_dy = 0

    def set_pos(self, x:int, y:int):
        self.old_x = self.x
        self.old_y = self.y
        self.x = x
        self.y = y

        if self.b1_down:
            self.b1_dx = self.x - self.old_x
            self.b1_dy = self.y - self.old_y

    def set_b1_state(self, state:bool):
        self.b1_down = state

    def move_node(self, node:MovableNode):
        node.move(self.b1_dx, self.b1_dy)
        # x = self.canvas.canvasx(node.x + self.b1_dx)
        # y = self.canvas.canvasy(node.y + self.b1_dy)
        x = node.x + self.b1_dx
        y = node.y + self.b1_dy
        node.set_pos(x, y)


class CanvasFrame():
    parent:tk.Frame
    canvas:tk.Canvas
    xsb:tk.Scrollbar
    ysb:tk.Scrollbar
    cd:CanvasData
    shared_objects:SharedObjects
    cmouse:CanvasMouse
    node_info_text_field:TextField
    dp = ConsoleDprint
    run_button:ttk.Button
    stop_button:ttk.Button
    select_callback_fn:Union[Callable, None]
    run_animate:bool
    label:str
    row:int
    width:int
    height:int
    virtual_canvas_size:int
    node_list:List
    selected_node:Union[MovableNode, None]
    test_node:Union[MovableNode, None]
    ENABLED = '!'+tk.DISABLED
    DISABLED = tk.DISABLED

    def __init__(self, parent:Union[tk.Frame, tk.LabelFrame], row:int, label:str, dprint:ConsoleDprint, width: int = 450, height: int = 400):
        self.parent = parent
        self.set_dprint(dprint)
        self.row = row
        self.label = label
        self.width = width
        self.height = height
        self.virtual_canvas_size = 1000
        self.build_view()
        self.node_list = []
        self.selected_node = None
        self.test_node = None
        self.select_callback_fn = None

    def set_SharedObjects(self, so:SharedObjects):
        self.shared_objects = so

    def set_select_callback_fn(self, tgt:Callable):
        self.select_callback_fn = tgt

    @staticmethod
    def rand_color() -> str:
        r = random.randrange(128, 255)
        g = random.randrange(128, 255)
        b = random.randrange(128, 255)
        return "#{:x}{:x}{:x}".format(r, g, b)

    def get_node_list(self) -> List:
        return self.node_list

    def set_dprint(self, con:ConsoleDprint):
        self.dp = con

    def build_view(self):
        print("build view")
        f:tk.LabelFrame = tk.LabelFrame(self.parent, text=self.label)

        f.grid(row=self.row, sticky="nsew", padx=5, pady=5)
        self.canvas = tk.Canvas(f, width=self.width, height=self.height, bg="white")
        self.cmouse = CanvasMouse(self.canvas)
        self.canvas.bind("<MouseWheel>", self.do_zoom)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self.canvas.bind("<Button-1>", self.button_1_pressed)
        self.canvas.bind("<ButtonRelease-1>", self.button_1_released)
        self.xsb = tk.Scrollbar(f, orient="horizontal", command=self.canvas.xview)
        self.ysb = tk.Scrollbar(f, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        self.canvas.configure(scrollregion=(self.width-self.virtual_canvas_size, self.height-self.virtual_canvas_size, self.virtual_canvas_size, self.virtual_canvas_size))

        self.xsb.grid(row=1, column=0, columnspan = 2, sticky="ew")
        self.ysb.grid(row=0, column=2, sticky="ns")
        self.canvas.grid(row=self.row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=5)
        #self.canvas.pack(padx=5, pady=5)
        #self.row += 2
        #self.run_button = ttk.Button(f, text="Run", command=self.run_animate)
        #self.run_button.grid(column=0, row=self.row, sticky="e", padx=5, pady=5)
        #self.stop_button = ttk.Button(f, text="Stop", command=self.stop_animate)
        #self.stop_button.grid(column=1, row=self.row, sticky="w", padx=5, pady=5)

    def setup(self, debug:bool = False, show_names:bool = True):
        self.dp.dprint("Setting up")
        self.cd = CanvasData(self.canvas)
        self.clear_Nodes()

        if debug:
            # create some nodes
            num_nodes = 200
            for i in range(num_nodes):
                color = "red"
                if i < num_nodes/3:
                    color = "blue"
                elif i > num_nodes *2/3:
                    color = "green"
                n = self.create_MoveableNode("{}_{}".format(color, i), color=color, size = 4, show_name=show_names)

            # connect some nodes
            connect = False
            if connect and num_nodes > 1:
                for i in range(int(num_nodes*1.5)):
                    n1:MovableNode = self.node_list[random.randrange(0, num_nodes - 1)]
                    n2:MovableNode = self.node_list[random.randrange(0, num_nodes - 1)]
                    self.connect_Nodes(n1, n2)

            #self.test_node = self.create_MoveableNode("TEST", size=30, color="#00CD00", show_name=show_names)
            #self.test_node.set_target(self.node_list[0])

        self.run_animate = False


    def create_MoveableNode(self, name:str, size=20, color:str="random", border:int = 50, x:float=0, y:float=0, dx:float=0, dy:float=0, show_name:bool = True) -> MovableNode:
        if x == 0 and y == 0:
            x = random.randrange(border, self.cd.right - border)
            y = random.randrange(border, self.cd.bottom - border)
        if color == "random":
            color = self.rand_color()
        n = MovableNode(name, self.cd, self.dp, color, size, x, y, dx, dy, show_name=show_name)
        self.add_Node(n)
        return n

    def add_Node(self, n:MovableNode):
        # go through the node list and lift all the MovableNodes
        mn:MovableNode
        for mn in self.node_list:
            if mn.type == NODE_TYPE.MOVEABLE:
                self.canvas.lift(mn.id)

        n.set_all_nodes_list(self.node_list)
        self.node_list.append(n)

    def clear_Nodes(self):
        self.node_list.clear()
        self.canvas.delete("all")

    def connect_Nodes(self, n1:MovableNode, n2:MovableNode) -> bool:
        if n1 != n2:
            n1.add_neighbor(n2)
            n2.add_neighbor(n1)
            return True
        return False

    def animate(self):
        elapsed = 1.0
        node:MovableNode
        for node in self.node_list:
            if node.type == NODE_TYPE.FORCE and self.run_animate:
                node.step(elapsed=elapsed)
            elif node.type == NODE_TYPE.MOVEABLE:
                # print("animating {}".format(node.name))
                node.step(elapsed=elapsed)
        # if self.run_animate:
        #     self.canvas.after(10, self.animate)
        self.canvas.after(10, self.animate)

    def handle_node_select(self, node_id:int, msg:str):
        if self.select_callback_fn != None:
            self.select_callback_fn(node_id, msg)

    def on_change(self):
        self.dp.dprint("Implement me!")

    def do_zoom(self, event:tk.Event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.cmouse.wheel = event.delta
        s = 1.0
        if event.delta < 0:
            s = 0.9
        elif event.delta > 0:
            s = 1.1
        self.canvas.scale(tk.ALL, x, y, s, s)

        node:MovableNode
        for node in self.node_list:
            node.set_screen_coords()


    def do_drag(self, event:tk.Event):
        x = int(self.canvas.canvasx(event.x))
        y = int(self.canvas.canvasy(event.y))
        #self.dp.dprint("pressed at ({}, {})/({}, {})".format(event.x, event.y, x, y))
        self.cmouse.set_pos(x, y)
        if self.selected_node != None:
            self.cmouse.move_node(self.selected_node)
            node:MovableNode
            for node in self.node_list:
                node.move(0,0)

    def select_node(self, item_id) -> bool:
        for n in self.node_list:
            if item_id == n.id:
                if self.selected_node == None:
                    self.selected_node = n
                elif self.selected_node != n:
                    self.canvas.itemconfig(self.selected_node.id, fill=self.selected_node.color)
                    self.selected_node.set_selected(False)
                    self.selected_node = n
                self.selected_node.set_selected(True)
                self.handle_node_select(n.id, "set selected node")
                return True
        return False

    def button_1_pressed(self, event:tk.Event):
        x = int(self.canvas.canvasx(event.x))
        y = int(self.canvas.canvasy(event.y))
        # self.dp.dprint("pressed at ({}, {})/({}, {})".format(event.x, event.y, x, y))
        self.cmouse.set_pos(x, y)
        self.cmouse.set_b1_state(True)
        id = self.canvas.find_closest(x, y)
        tags = self.canvas.gettags(id)
        match = False
        if len(tags) > 0:
            tag = tags[0]
            self.dp.dprint("selecting = id:{} tags:{}".format(id, tags))
            n:MovableNode
            item = self.canvas.find_withtag(tag)[0]
            match = self.select_node(item)
        if not match and self.selected_node != None:
            self.handle_node_select(-1, "No node clicked on")
            self.canvas.itemconfig(self.selected_node.id, fill=self.selected_node.color)
            self.selected_node = None
        else:
            self.dp.dprint("selected node = [{}]".format(self.selected_node.name))


    def button_1_released(self, event:tk.Event):
        self.dp.dprint("B1 released at ({}, {})".format(event.x, event.y))
        self.cmouse.set_b1_state(False)

    def run_animate(self):
        self.run_button.state([self.DISABLED])
        self.stop_button.state([self.ENABLED])
        self.run_animate = True
        self.animate()

    def stop_animate(self):
        self.stop_button.state([self.DISABLED])
        self.run_button.state([self.ENABLED])
        self.run_animate = False

    def get_next_row(self):
        return self.row + 1

def set_random_target(cf:CanvasFrame):
    next_node:MovableNode = random.choice(cf.node_list)
    cf.test_node.set_target(next_node)
    cf.test_node.clear_neighbors()
    cf.test_node.add_neighbor(next_node)
    cf.dp.dprint("Set target = {}".format(next_node.name))

def print_data(cf:CanvasFrame):
    tst = cf.test_node
    print("\n{}: ({:.2f}. {:.2f})".format(tst.name, tst.x, tst.y))
    tgt = cf.test_node.target
    print("{}: ({:.2f}. {:.2f})".format(tgt.name, tgt.x, tgt.y))
    dx = tgt.x-tst.x
    dy = tgt.y-tst.y
    dist = math.sqrt(dx*dx + dy*dy)
    print("Difference: ({:.2f}. {:.2f})".format(dx, dy))
    print("Distance: {:.2f}".format(dist))

def change_random_node(cf:CanvasFrame):
    fn:MovableNode = random.choice(cf.node_list)
    if fn.type == NODE_TYPE.FORCE:
        cf.dp.dprint("Before: Node = {}, size = {:.3f}, mass = {:.3f}".format(fn.name, fn.size, fn.mass))
        scalar = 1.0 + random.random()
        fn.adjust_mass_size(scalar=scalar)
        cf.select_node(fn.id)
        cf.dp.dprint("After: Node = {}, size = {:.3f}, mass = {:.3f}".format(fn.name, fn.size, fn.mass))
    else:
        cf.dp.dprint("Node = {}, size = {:.3f}".format(fn.name, fn.size))


def implement_me():
    print("implement me!")


def main():
    print("CanvasFrame")
    window = tk.Tk()
    window.title("CanvasFrame testbed")
    # window.geometry("500x650")

    wrapper = tk.Frame(window)
    wrapper.pack()
    dp = ConsoleDprint()
    cf = CanvasFrame(wrapper, 0, "Graph", dp, width=450, height=400)


    button_wrapper = tk.LabelFrame(wrapper, text="Buttons")
    button_wrapper.grid(row=1, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
    b = Buttons(button_wrapper, 0, "Commands:", label_width=10, sticky="e")
    b.add_button("Random Target", lambda : set_random_target(cf))
    b.add_button("Print Node Data", lambda : print_data(cf))
    b.add_button("Change Random Node", lambda: change_random_node(cf))

    dp.create_tk_console(wrapper, 2, char_width=50)

    cf.setup(debug=True, show_names=False)

    window.mainloop()

if __name__ == "__main__":
    main()
