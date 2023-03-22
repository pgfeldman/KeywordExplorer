from math import pi, sin, cos, radians
from typing import Tuple, List

import numpy as np
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import GeomNode, CullFaceAttrib
from panda3d.core import GeomVertexArrayFormat
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import LVecBase4f
from panda3d.core import LVector3

from keyword_explorer.Panda3D.DefinedColors import DefinedColors


class ShapePrimitives():
    def __init__(self):
        self.colors = DefinedColors()

    def normalized(self, *args):
        myVec = LVector3(*args)
        myVec.normalize()
        return myVec

    def calc_normal_vec(self, v1: Tuple[float, float, float], v2: Tuple[float, float, float],
                        normal_direction: float = 1.0) -> Tuple[float, float, float]:
        a = np.array(v1)
        b = np.array(v2)
        result = np.cross(a, b) * normal_direction
        t = tuple(result)
        return t

    def create_tmesh(self, num_indices: int, vertex_list: List, normal_list: List, color_list: List,
                     texture_list: List) -> Geom:
        format_array = GeomVertexArrayFormat()
        format_array.addColumn("vertex", 3, Geom.NTFloat32, Geom.CPoint)
        format_array.addColumn("normal", 3, Geom.NTFloat32, Geom.CNormal)
        format_array.addColumn("color", 4, Geom.NTFloat32, Geom.CColor)
        format_array.addColumn("texcoord", 2, Geom.NTFloat32, Geom.CTexcoord)

        format = GeomVertexFormat()
        format.add_array(format_array)
        format = GeomVertexFormat.registerFormat(format)

        vdata = GeomVertexData('cylinder', format, Geom.UHStatic)
        vdata.setNumRows(len(vertex_list))

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')

        # print("rows: vertex = {}, normal = {}, color = {}, texture = {}".format(len(vertex_list), len(normal_list), len(color_list), len(normal_list)))

        for v in vertex_list:
            vertex.addData3f(v)
        for n in normal_list:
            normal.addData3f(n)
        for c in color_list:
            color.addData4f(c)
        for t in texture_list:
            texcoord.addData2f(t)

        tris = GeomTriangles(Geom.UHStatic)
        for i in range(num_indices):
            tris.addVertices(i, i + 1, i + 2)
            tris.addVertices(i + 2, i + 1, i + 3)

        tmesh = Geom(vdata)
        tmesh.addPrimitive(tris)
        return tmesh

    def create_disk(self, segments: int = 18, radius: float = 1, inner_radius: float = 0.1, zpos=0,
                    normal_direction: float = 1.0, cname: str = None, dither: float = 0.25):
        cval = self.colors.get_color("black")
        if cname != None:
            cval = self.colors.get_color(cname)

        # make lists that will contain the data that we'll use in an agnostic format. This lets us know how many tuples we have
        step = 2 * pi / segments
        angle = -pi
        vertex_list = []
        normal_list = []
        tex_list = []
        color_list = []
        max_val = radius
        min_val = -radius
        val_range = max_val - min_val
        for i in range(segments + 2):
            # print("angle = {}".format(degrees(angle)))
            tx = (cos(angle) * radius - min_val) / val_range
            ty = (sin(angle) * radius - min_val) / val_range
            tx2 = (cos(angle) * inner_radius - min_val) / val_range
            ty2 = (sin(angle) * inner_radius - min_val) / val_range
            x1 = cos(angle) * radius
            y1 = sin(angle) * radius
            z = zpos
            x2 = cos(angle) * inner_radius
            y2 = sin(angle) * inner_radius

            xn1 = cos(angle)
            yn1 = cos(angle)
            angle += step
            xn2 = cos(angle)
            yn2 = cos(angle)
            n = self.calc_normal_vec((xn1, yn1, z), (xn2, yn2, z), normal_direction)

            vertex_list.append((x1, y1, z))
            normal_list.append(self.normalized(n))
            color_list.append(self.colors.jiggle_color(cval, scalar=dither))
            tex_list.append((tx, ty))

            vertex_list.append((x2, y2, z))
            normal_list.append(self.normalized(n))
            color_list.append(self.colors.jiggle_color(cval, scalar=dither))
            tex_list.append((tx2, ty2))

        tmesh = self.create_tmesh(2 * segments, vertex_list, normal_list, color_list, tex_list)
        snode = GeomNode("disk")
        snode.addGeom(tmesh)
        return snode

    def create_cylinder(self, segments: int = 18, radius: float = 1, zmax: float = 1, zmin: float = -1, tmin: float = 0,
                        tmax: float = 1, cname: str = None, dither: float = 0.20) -> GeomNode:
        return self.create_conic(segments=segments, rzmax=radius, zmax=zmax, rzmin=radius, zmin=zmin, tmin=tmin,
                                 tmax=tmax, cname=cname, dither=dither)

    def create_sphere(self, lat_segs: int = 18, lon_segs: int = 18, radius: float = 1.0, cname: str = None, cvec:LVecBase4f = None) -> GeomNode:
        lat_step_deg = 180.0 / lat_segs
        lat = lat_step_deg / 2.0
        snode = GeomNode("sphere")
        while lat < (180 - lat_step_deg):
            amax = radians(lat)
            zmax = cos(amax) * radius
            rzmax = sin(amax) * radius
            t1 = lat / 180
            lat += lat_step_deg
            t2 = lat / 180
            # print("t1 = {}, t2 = {}".format(t1, t2))
            amin = radians(lat)
            zmin = cos(amin) * radius
            rzmin = sin(amin) * radius
            conic = self.create_conic(lon_segs, rzmax, zmax, rzmin, zmin, t1, t2, cname=cname, cvec=cvec)
            snode.addChild(conic)
        return snode

    def create_conic(self, segments: int = 18, rzmax: float = 1, zmax: float = 1, rzmin: float = 0.1, zmin: float = -1,
                     tmin: float = 0, tmax: float = 1, cname: str = None, dither: float = 0.20, cvec:LVecBase4f = None) -> GeomNode:
        cval = self.colors.get_color("black")
        if cname != None:
            cval = self.colors.get_color(cname)
        elif cvec != None:
            cval = cvec

        # make lists that will contain the data that we'll use in an agnostic format. This lets us know how many tuples we have
        step = 2 * pi / segments
        angle = -pi
        vertex_list = []
        normal_list = []
        tex_list = []
        color_list = []
        tex_step = 1 / (segments + 2)
        for i in range(segments + 2):
            # print("angle = {}".format(degrees(angle)))
            x1 = cos(angle) * rzmax
            y1 = sin(angle) * rzmax
            z1 = zmax
            x2 = cos(angle) * rzmin
            y2 = sin(angle) * rzmin
            z2 = zmin
            angle += step
            # get the vectors to calc the cross product
            xv1 = x1 - cos(angle) * rzmax
            yv1 = y1 - sin(angle) * rzmax
            xv2 = x2 - x1
            yv2 = y2 - y1
            zv2 = zmax - zmin
            n = self.calc_normal_vec((xv1, yv1, 0), (xv2, yv2, zv2))
            n = self.normalized(n)
            vertex_list.append((x1, y1, z1))
            normal_list.append(n)
            color_list.append(self.colors.jiggle_color(cval, scalar=dither))
            tex_list.append((i * tex_step, tmin))
            vertex_list.append((x2, y2, z2))
            normal_list.append(n)
            color_list.append(self.colors.jiggle_color(cval, scalar=dither))
            tex_list.append((i * tex_step, tmax))

        tmesh = self.create_tmesh(2 * segments, vertex_list, normal_list, color_list, tex_list)
        snode = GeomNode("cylinder")
        snode.addGeom(tmesh)
        return snode

    def create_square(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float,
                      cval: LVecBase4f = None) -> Geom:
        format = GeomVertexFormat.getV3n3cpt2()
        vdata = GeomVertexData('square', format, Geom.UHDynamic)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')

        # make sure we draw the sqaure in the right plane
        if x1 != x2:
            vertex.addData3(x1, y1, z1)
            vertex.addData3(x2, y1, z1)
            vertex.addData3(x2, y2, z2)
            vertex.addData3(x1, y2, z2)

            normal.addData3(self.normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
            normal.addData3(self.normalized(2 * x2 - 1, 2 * y1 - 1, 2 * z1 - 1))
            normal.addData3(self.normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
            normal.addData3(self.normalized(2 * x1 - 1, 2 * y2 - 1, 2 * z2 - 1))

        else:
            vertex.addData3(x1, y1, z1)
            vertex.addData3(x2, y2, z1)
            vertex.addData3(x2, y2, z2)
            vertex.addData3(x1, y1, z2)

            normal.addData3(self.normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
            normal.addData3(self.normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z1 - 1))
            normal.addData3(self.normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
            normal.addData3(self.normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z2 - 1))

        # adding different colors to the vertex for visibility

        if color == None:
            cval = self.colors.get_color("black")

        color.addData4f(cval)
        color.addData4f(cval)
        color.addData4f(cval)
        color.addData4f(cval)

        texcoord.addData2f(0.0, 1.0)
        texcoord.addData2f(0.0, 0.0)
        texcoord.addData2f(1.0, 0.0)
        texcoord.addData2f(1.0, 1.0)

        # Quads aren't directly supported by the Geom interface
        # you might be interested in the CardMaker class if you are
        # interested in rectangle though
        tris = GeomTriangles(Geom.UHDynamic)
        tris.addVertices(0, 1, 3)
        tris.addVertices(1, 2, 3)

        square = Geom(vdata)
        square.addPrimitive(tris)
        return square

    def create_cube(self, size: float = 1.0, cname: str = "gray", dither: float = 0.25) -> GeomNode:
        min = -size / 2.0
        max = size / 2.0

        snode = GeomNode('square')

        cval = self.colors.get_color(cname)

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(min, min, min, max, max, min, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(min, min, max, max, max, max, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(min, min, min, min, max, max, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(max, min, min, max, max, max, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(min, min, min, max, min, max, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(min, max, min, max, max, max, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        return snode

    def create_rect_cube(self, x_min:float = -1.0, y_min:float = -1.0, z_min:float = -1.0,
                         x_max:float = 1.0, y_max:float = 1.0, z_max:float = 1.0,
                         cname: str = "gray", dither: float = 0.25) -> GeomNode:

        snode = GeomNode('square')

        cval = self.colors.get_color(cname)

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(x_min, y_min, z_min, x_max, y_max, z_min, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(x_min, y_min, z_max, x_max, y_max, z_max, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(min, min, min, min, max, max, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(max, min, min, max, max, max, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(min, min, min, max, min, max, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        cval2 = self.colors.jiggle_color(cval, scalar=dither)
        square = self.create_square(min, max, min, max, max, max, cval=cval2)
        snode.addGeom(square)
        snode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        return snode
