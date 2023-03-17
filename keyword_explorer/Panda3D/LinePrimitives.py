from panda3d.core import LVecBase4f
from panda3d.core import LineSegs
from panda3d.core import NodePath
from panda3d.core import LVecBase4f, LVecBase3f
from typing import Tuple, List, Dict

from keyword_explorer.Panda3D.DefinedColors import DefinedColors


class LinePrimitives:
    colors = None
    prim_dict:Dict

    def __init__(self):
        self.colors = DefinedColors()
        self.prim_dict = {}

    def get_LineSeg(self, name) -> LineSegs:
        if name in self.prim_dict:
            return self.prim_dict[name]
        return None

    def create_polyline(self, name:str, points:List[LVecBase3f], line_thickness:float=1.0, color:LVecBase4f=LVecBase4f(1, 1, 1, 1)) -> NodePath:
        ls = LineSegs(name)
        self.prim_dict[name] = ls
        ls.setThickness(line_thickness)

        ls.setColor(color)
        ls.moveTo(points[0])
        for i in range(1, len(points)):
            ls.drawTo(points[i])

        node = ls.create()
        return NodePath(node)

    def create_line(self, start:LVecBase3f, end:LVecBase3f, name:str, line_thickness:float=1.0, color:LVecBase4f=LVecBase4f(0.7, 0.7, 0.7, 1)) -> NodePath:
        ls = LineSegs(name)
        self.prim_dict[name] = ls
        ls.setThickness(line_thickness)

        ls.setColor(color)
        ls.moveTo(start)
        ls.drawTo(end)

        node = ls.create()
        return NodePath(node)

    def create_axis(self, line_thickness: float = 1.0, size:float = 5) -> NodePath:
        ls = LineSegs()
        ls.setThickness(line_thickness)

        # X axis
        ls.setColor(self.colors.red)
        ls.moveTo(0.0, 0.0, 0.0)
        # ls.drawTo(1.0, 0.0, 0.0)
        ls.drawTo(size, 0.0, 0.0)

        # Y axis
        ls.setColor(self.colors.blue)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(0.0, size, 0.0)

        # Z axis
        ls.setColor(self.colors.green)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(0.0, 0.0, size)

        node = ls.create()
        return NodePath(node)

    def create_grid(self, line_thickness: float = 1.0, segments: int = 10, size: float = 2.0, color: LVecBase4f = None,
                    plane: str = "XY") -> NodePath:
        p = plane.lower()
        ls = LineSegs()
        ls.setThickness(line_thickness)

        step = size / segments
        start = -size / 2.0
        stop = size / 2.0
        ls.setColor(self.colors.get_color(color))
        if p == "xy":
            x = start
            for i in range(segments + 1):
                ls.moveTo(x, start, 0)
                ls.drawTo(x, stop, 0)
                ls.moveTo(start, x, 0)
                ls.drawTo(stop, x, 0)
                x += step
        elif p == "xz":
            x = start
            for i in range(segments + 1):
                ls.moveTo(x, 0, start)
                ls.drawTo(x, 0, stop)
                ls.moveTo(start, 0, x)
                ls.drawTo(stop, 0, x)
                x += step
        elif p == "yz":
            x = start
            for i in range(segments + 1):
                ls.moveTo(0, x, start)
                ls.drawTo(0, x, stop)
                ls.moveTo(0, start, x)
                ls.drawTo(0, stop, x)
                x += step

        node = ls.create()
        return NodePath(node)
