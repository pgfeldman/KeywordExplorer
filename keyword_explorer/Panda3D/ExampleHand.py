from direct.gui.DirectGui import *
import pandas as pd
from panda3d.core import TextNode, LineSegs, NodePath, TransparencyAttrib, WindowProperties, PerspectiveLens
from panda3d.core import LVecBase4f, LVecBase3f, GeomNode
import numpy as np
import random
import math
from typing import List, Dict

from keyword_explorer.Panda3D.Pandas_main import Pandas_main
from keyword_explorer.Panda3D.ShapePrimitives import ShapePrimitives
from keyword_explorer.Panda3D.LinePrimitives import LinePrimitives
from keyword_explorer.Panda3D.DefinedColors import DefinedColors

class ExampleHand (Pandas_main):
    text_node_dict:Dict
    palm_node: NodePath
    finger_1a_node: NodePath
    finger_1b_node: NodePath

    def add_setups(self, parent: NodePath):
        tnode:NodePath
        self.palm_node:NodePath
        render_node:GeomNode
        self.palm_node = parent.attachNewNode("palm_node")
        self.palm_node.attachNewNode(self.sp.create_cube())
        self.palm_node.set_p(45)
        #make the first finger knuckle
        self.finger_1a_node = self.palm_node.attachNewNode("finger1aTranslate")
        self.finger_1a_node.setPos((0, 0, 1))
        self.finger_1a_node.set_p(45)
        self.finger_1a_node.attachNewNode(self.sp.create_cube())
        #make the second finger knuckle
        self.finger_1b_node = self.finger_1a_node.attachNewNode("finger1bTranslate")
        self.finger_1b_node.setPos((0, 0, 1))
        self.finger_1b_node.set_p(45)
        scaled_finger_node:NodePath
        scaled_finger_node = self.finger_1b_node.attachNewNode("scaled_finger_node")
        scaled_finger_node.setScale((1, 1, 2))
        scaled_finger_node.attachNewNode(self.sp.create_cube())



def main():
    r = ExampleHand()
    r.run()

if __name__ == "__main__":
    main()