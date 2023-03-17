from direct.gui.DirectGui import *
from panda3d.core import TextNode, LineSegs, NodePath, TransparencyAttrib, WindowProperties, PerspectiveLens
from panda3d.core import GeomNode, Fog
from panda3d.core import LVecBase4f, LVecBase3f
from keyword_explorer.utils.NetworkxGraphing import NetworkxGraphing
from tkinter import filedialog
from datetime import datetime
import math
from typing import List, Dict, Union

from keyword_explorer.Panda3D.Pandas_main import Pandas_main

class Xform:
    terrain_segments:int
    terrain_min:int
    terrain_max:int
    terrain_range:int
    terrain_step:int
    terrain_min_z:float
    terrain_max_z:float
    terrain_z_range:float

    x_range:float
    y_range:float
    z_range:float
    x_scalar:float
    y_scalar:float
    z_scalar:float

    min_x:float
    max_x:float
    min_y:float
    max_y:float
    min_z:float
    max_z:float

    def __init__(self, segs:int = 25, min:int = -25, max:int = 25, step:int = 2):
        self.terrain_segments = segs
        self.terrain_min = min
        self.terrain_max = max
        self.terrain_range = self.terrain_max - self.terrain_min
        self.terrain_step = step
        self.min_x = float('inf')
        self.max_x = float('-inf')
        self.min_y = float('inf')
        self.max_y = float('-inf')
        self.min_z = float('inf')
        self.max_z = float('-inf')
        self.terrain_min_z = 1
        self.terrain_max_z = 10
        self.terrain_z_range = self.terrain_max_z - self.terrain_min_z

    def update(self, x:float, y:float, z:float):
        self.min_x = min(self.min_x, x)
        self.max_x = max(self.max_x, x)
        self.min_y = min(self.min_y, y)
        self.max_y = max(self.max_y, y)
        self.min_z = min(self.min_z, z)
        self.max_z = max(self.max_z, z)
        self.x_range = self.max_x - self.min_x
        self.y_range = self.max_y - self.min_y
        self.z_range = self.max_z - self.min_z
        if self.x_range > 0 and self.y_range > 0 and self.z_range > 0:
            self.x_scalar = self.terrain_range/self.x_range
            self.y_scalar = self.terrain_range/self.y_range
            self.z_scalar = self.terrain_z_range/self.z_range

    def xform_x(self, x:float) -> float:
        return (x - self.min_x)*self.x_scalar + self.terrain_min

    def xform_y(self, y:float) -> float:
        return (y - self.min_y)*self.y_scalar + self.terrain_min

    def xform_z(self, z:float) -> float:
        return (z - self.min_z)*self.z_scalar + self.terrain_min_z


class TerrainFromGML (Pandas_main):
    text_screen_dict:Dict
    text_node_dict:Dict
    node_attr_dict:Dict
    lit_terrain_node:NodePath
    unlit_terrain_node:NodePath
    nxg:Union[NetworkxGraphing, None]
    xf:Xform

    def __init__(self):
        Pandas_main.__init__(self)
        self.setFrameRateMeter(True)

        w, h = 760, 512
        props = WindowProperties()
        props.setTitle("TerrainFromGML v 1.11.2022")
        props.setSize(w, h)
        self.setBackgroundColor(self.sp.colors.dark_gray)
        lens = PerspectiveLens()
        lens.setAspectRatio(w/h)
        self.cam.node().setLens(lens)
        self.win.requestProperties(props)

    def reset(self):
        super().reset()
        print("TerrainFromGML.reset()")
        self.xf = Xform()
        self.text_screen_dict = {}
        self.text_node_dict = {}
        self.node_attr_dict = {}
        self.nxg = None

    def calc_z(self, x:float, y:float, offset:float = 0, scalar:float = 1.0, inner_scalar:float = 5.0) -> float:
        z = 0
        for name, attrs in self.node_attr_dict.items():
            x2 = attrs['new_x']
            y2 = attrs['new_y']
            z2 = attrs['new_z']
            z2 = math.sqrt(z2)*inner_scalar # Changes the shape of the terrain
            dist = math.hypot(x-x2, y-y2)
            dist = math.sqrt(dist*0.5)*inner_scalar
            z = max(z2 - dist, z)

        return z * scalar + offset

    def get_min_max_z(self, offset:float = 0, scalar:float = 1.0) -> (float, float):
        min_zval = self.xf.xform_z(self.xf.min_z) * scalar + offset
        max_zval = self.xf.xform_z(self.xf.max_z)* scalar + offset
        return (min(min_zval, max_zval), max(min_zval, max_zval))

    def create_terrain_grid(self, name:str, segments:int, xstart:float, ystart:float, xstep:float = 1.0,
                            ystep:float = 1.0, z_offset = 0.1, z_scalar = 1.0, line_thickness:float=1.0,
                            color:LVecBase4f=LVecBase4f(0.5, 0.5, 0.5, 1)) -> GeomNode:
        ls = LineSegs(name)
        ls.setThickness(line_thickness)
        ls.setColor(color)
        x1 = xstart
        for i in range(segments + 1):
            y1 = ystart + ystep * i
            z1 = self.calc_z(x1, y1, offset=z_offset, scalar=z_scalar)
            ls.moveTo(LVecBase3f(x1, y1, z1))
            for j in range(segments + 2):
                x1 = xstart + xstep*j
                z1 = self.calc_z(x1, y1, offset=z_offset, scalar=z_scalar)
                if j == 0:
                    ls.moveTo(LVecBase3f(x1, y1, z1))
                else:
                    ls.drawTo(LVecBase3f(x1, y1, z1))

        y1 = ystart
        for i in range(segments + 2):
            x1 = xstart + xstep*i
            z1 = self.calc_z(x1, y1, offset=z_offset, scalar=z_scalar)
            ls.moveTo(LVecBase3f(x1, y1, z1))
            for j in range(segments + 1):
                y1 = ystart + ystep * j
                z1 = self.calc_z(x1, y1, offset=z_offset, scalar=z_scalar)
                if j == 0:
                    ls.moveTo(LVecBase3f(x1, y1, z1))
                else:
                    ls.drawTo(LVecBase3f(x1, y1, z1))

        node = ls.create()
        return NodePath(node).node()

    def create_terrain_strip(self, segments, xstart:float, ystart:float, xstep:float = 1.0, ystep:float = 1.0,
        tmin:float = 0, tmax:float = 1, dither:float = 0.20, c1:LVecBase4f = LVecBase4f(0.8, 0.8, 0.8, 1),
        c2:LVecBase4f = LVecBase4f(0.8, 0.8, 0.8, 1), z_scalar:float = 1.0) -> GeomNode:


        vertex_list = []
        normal_list = []
        tex_list = []
        color_list = []
        tex_step = 1 / (segments + 2)
        min_zval, max_zval = self.get_min_max_z(scalar=z_scalar)
        for i in range(segments + 2):
            x1 = xstart + xstep*i
            y1 = ystart
            z1 = self.calc_z(x1, y1, scalar=z_scalar)

            x2 = xstart + xstep*i
            y2 = ystart + ystep
            z2 = self.calc_z(x2, y2, scalar=z_scalar)

            x3 = xstart + xstep + i + 1
            y3 = ystart
            z3 = self.calc_z(x3, y3, scalar=z_scalar)

            # get the vectors to calc the cross product
            xv1 = x2 - x1
            yv1 = y2 - y1
            zv1 = z2 - z1

            xv2 = x3 - x1
            yv2 = y3 - y1
            zv2 = z3 - z1
            n = self.sp.calc_normal_vec((xv1, yv1, zv1), (xv2, yv2, zv2))
            n = self.sp.normalized(n)
            vertex_list.append((x1, y1, z1))
            normal_list.append(n)
            c = self.sp.colors.adjust_color(c1=c1, c2=c2, val=z1, min_val=min_zval, max_val=max_zval)
            #color_list.append(self.sp.colors.jiggle_color(cvec, scalar=dither))

            color_list.append(c)

            tex_list.append((i * tex_step, tmin))
            vertex_list.append((x2, y2, z2))
            normal_list.append(n)
            c = self.sp.colors.adjust_color(c1=c1, c2=c2, val=z2, min_val=min_zval, max_val=max_zval)
            #color_list.append(self.sp.colors.jiggle_color(cvec, scalar=dither))
            color_list.append(c)
            # color_list.append(self.sp.colors.red)
            tex_list.append((i * tex_step, tmax))

        tmesh = self.sp.create_tmesh(2 * segments, vertex_list, normal_list, color_list, tex_list)
        snode = GeomNode("tmesh")
        snode.addGeom(tmesh)
        return snode

    def create_terrain(self, lit_node:NodePath, unlit_node:NodePath = None):
        keys = self.nxg.get_node_names()
        if unlit_node == None:
            unlit_node = lit_node

        # determine the range that the Xform will work over
        for name in keys:
            attrs = self.nxg.get_node_attributes(name)
            self.node_attr_dict[name] = attrs
            # print("{} = {}".format(name, attrs))
            gd = attrs['graphics']
            x = gd['x']
            y = gd['y']
            z = 1
            if 'weight' in attrs:
                z = float(attrs['weight'])
            else:
                z = len(self.nxg.find_closest_neighbors())
            self.xf.update(x, y, z)

        # apply the Xform
        for name, attrs in self.node_attr_dict.items():
            gd = attrs['graphics']
            x = gd['x']
            y = gd['y']
            z = 1
            if 'weight' in attrs:
                z = float(attrs['weight'])
            else:
                z = len(self.nxg.find_closest_neighbors())
            new_x = self.xf.xform_x(x)
            new_y = self.xf.xform_y(y)
            new_z = self.xf.xform_z(z)
            attrs['new_x'] = new_x
            attrs['new_y'] = new_y
            attrs['new_z'] = new_z
            print("{} = {}".format(name, attrs))


        # draw the terrain
        z_scalar = 1.5
        tstep = self.xf.terrain_step
        tmin = self.xf.terrain_min - tstep * 10
        tmax = self.xf.terrain_max  + tstep * 10
        tsegments = int((tmax - tmin)/tstep) # self.xf.terrain_segments
        for ystart in range(tmin, tmax, tstep):
            node = self.create_terrain_strip(tsegments, tmin, ystart, xstep=tstep, ystep=tstep, z_scalar=z_scalar,
                                             c1=self.sp.colors.red, c2=self.sp.colors.dark_gray)
            lit_node.attachNewNode(node)

        node = self.create_terrain_grid("terrain_grid", tsegments, tmin, tmin, xstep=tstep, ystep=tstep, z_scalar=z_scalar)
        unlit_node.attachNewNode(node)

        # add the names at the right place
        ls = LineSegs("pointers")
        ls.setThickness(2)
        for name, attrs in self.node_attr_dict.items():
            node = TextNode(name)
            node.setText(name)
            tnp:NodePath = unlit_node.attachNewNode(node)
            #tnp.setPos(self.world_node, random.randint(-25, 25), random.randint(-25, 25), 3)
            tnp.setScale(1.0)
            x = attrs['new_x']
            y = attrs['new_y']
            offset = 0.5
            z = self.calc_z(x, y, scalar=z_scalar, offset=offset)
            tnp.setPos(self.world_node, x, y, max(z, offset))
            ls.moveTo(LVecBase3f(x, y, z-offset))
            ls.drawTo(LVecBase3f(x, y, 0))
            self.text_node_dict[name] = tnp
        node = ls.create()
        unlit_node.attachNewNode(node)


    def stage_inits(self):
        # super().stage_inits() # Normally we would call this, but we want bigger grids
        self.world_node.setTransparency(TransparencyAttrib.MAlpha)
        self.axis_node = self.world_node.attachNewNode("Axis")
        self.grid_node = self.world_node.attachNewNode("Grid")
        self.axis_node.attachNewNode(self.lp.create_axis(4.0, size=25).node())
        self.grid_node.attachNewNode(self.lp.create_grid(size=50, color="trans_cyan").node())
        self.grid_node.attachNewNode(self.lp.create_grid(size=50, color="trans_magenta", plane="xz").node())
        self.grid_node.attachNewNode(self.lp.create_grid(size=50, color="trans_yellow", plane="yz").node())

        self.lit_terrain_node = self.world_node.attachNewNode("Lit_terrain")
        self.unlit_terrain_node = self.world_node.attachNewNode("Unlit_terrain")
        tl = self.add_directional_light("Terrain_light", self.lit_terrain_node, self.lit_terrain_node)
        tl.setHpr(380, 270, 0)

        self.camera.setPos(0, 0, 0)
        self.camera.setHpr(0, 0, 0)
        self.world_translate_node.setPos(0, 100, -5)

    def add_tasks(self):
        self.accept("l", self.load_gml_task)

        self.accept("shift-h", lambda : self.increment_light_heading_task(-10))
        self.accept("h", self.increment_light_heading_task)
        self.accept("shift-p", lambda: self.increment_light_pitch_task(-10))
        self.accept("p", self.increment_light_pitch_task)
        self.accept("a", lambda: self.show_hide_node_task(self.axis_node))
        self.accept("g", lambda: self.show_hide_node_task(self.grid_node))
        self.accept("t", self.show_hide_text_task)

        self.taskMgr.add(self.update_task, "update_task")

    def implement_me(self, val=0):
        print("implement me! ({})".format(val))

    def add_terminate(self):
        print("terminating")
        self.taskMgr.remove("update_task")

    def setup_text(self):
        # font = self.loader.loadFont('C:/Windows/Fonts/Courier New.ttf')
        copyright_str = "© Philip Feldman ({})".format(datetime.now().year)
        # copyright_str = "© ASRC Federal ({})".format(datetime.now().year)
        OnscreenText(text="TerrainFromGML",
                             style=1, fg=(1, 1, 1, 1), pos=(-0.65, 0.1), scale=.07,
                             parent=self.a2dBottomRight, align=TextNode.ALeft)
        OnscreenText(text=copyright_str,
                             style=1, fg=(1, 1, 1, 1), pos=(-0.65, 0.05), scale=.05,
                             parent=self.a2dBottomRight, align=TextNode.ALeft)
        names = ['toggle [a]xis', 'toggle [g]rid', 'toggle [t]ext', '[l]oad GML', '[h]eading', '[p]itch']
        ypos = -.1
        for n in names:
            text = "{}: ".format(n)
            node = OnscreenText(text=text, style=1, fg=(1, 1, 1, 1), pos=(0.05, ypos),
                                scale=.05, parent=self.a2dTopLeft, align=TextNode.ALeft)
            self.text_screen_dict[n] = node
            # self.text_node_dict[n] = node
            ypos -= 0.06

    def show_hide_node_task(self, node:NodePath):
        if node.isHidden():
            node.show()
        else:
            node.hide()

    def show_hide_text_task(self):
        node:NodePath
        for name, node in self.text_screen_dict.items():
            self.show_hide_node_task(node)

    def increment_light_heading_task(self, step:int=10):
        tl = self.get_directional_light("Terrain_light")
        if tl != None:
            hpr = tl.getHpr()
            hpr[0] += step
            tl.setHpr(hpr)
        return self.task_state

    def increment_light_pitch_task(self, step:int=10):
        tl = self.get_directional_light("Terrain_light")
        if tl != None:
            hpr = tl.getHpr()
            hpr[1] += step
            tl.setHpr(hpr)
        return self.task_state


    def load_gml_task(self):
        print("load_gml_task")
        filename = filedialog.askopenfilename(filetypes=(("GML files", "*.gml"),("All Files", "*.*")), title="Load GML Files")
        if filename:
            print("opening {}".format(filename))
            self.nxg = NetworkxGraphing("test")
            self.nxg.read_gml(filename)
            self.nxg.print_stats()
            self.create_terrain(self.lit_terrain_node, self.unlit_terrain_node)

    def update_text(self, tag:str, val:any):
        if tag in self.text_screen_dict:
            n:TextNode = self.text_screen_dict[tag]
            if isinstance(val, float):
                n.setText('{}: {:.3f}'.format(tag, val))
            else:
                n.setText('{}: {}'.format(tag, val))

    def update_task(self, task):
        tl = self.get_directional_light("Terrain_light")
        if tl != None:
            hpr = tl.getHpr()
            self.update_text('[h]eading', hpr[0])
            self.update_text('[p]itch', hpr[1])

        yaw = self.world_yaw_node.getH()
        pitch = self.world_pitch_node.getP()

        tnp:NodePath
        for key, tnp in self.text_node_dict.items():
            tnp.setH(-yaw)
            tnp.setP(-pitch)
        return self.task_state

def main():
    r = TerrainFromGML()
    r.run()

if __name__ == "__main__":
    main()
