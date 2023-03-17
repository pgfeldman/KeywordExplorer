import os, sys

from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import TextNode, NodePath, TransparencyAttrib, AudioManager, DirectionalLight

from keyword_explorer.Panda3D.LinePrimitives import LinePrimitives
from keyword_explorer.Panda3D.MouseEventHandler import MouseEventHandler
from keyword_explorer.Panda3D.ShapePrimitives import ShapePrimitives

from typing import Dict, Tuple, Union


class Pandas_main(ShowBase):
    lp: Union[None, LinePrimitives]
    sp: Union[None, ShapePrimitives]
    meh: Union[None, MouseEventHandler]
    yaw_world_node: Union[None, NodePath]
    pitch_world_node: Union[None, NodePath]
    roll_world_node: Union[None, NodePath]
    world_node: Union[None, NodePath]
    axis_node: Union[None, NodePath]
    grid_node: Union[None, NodePath]
    light_dict: Dict
    counter = 0
    task_state = Task.cont

    def __init__(self):
        ShowBase.__init__(self)
        self.reset()
        self.add_graphic_inits()

        self.lp = LinePrimitives()
        self.sp = ShapePrimitives()
        self.meh = MouseEventHandler(.01)

        self.disableAllAudio()
        self.disableMouse()

        self.setup_text()

        self.world_translate_node = self.render.attachNewNode("world_translate")
        self.world_pitch_node = self.world_translate_node.attachNewNode("world_pitch_node")
        self.world_yaw_node = self.world_pitch_node.attachNewNode("world_yaw_node")
        self.world_roll_node = self.world_yaw_node.attachNewNode("world_roll_node")
        self.world_node = self.world_roll_node.attachNewNode("world")

        self.stage_inits()
        self.add_setups(self.world_node)

        # Add the move_world_task procedure to the task manager.
        self.taskMgr.add(self.move_world_task, "move_world_task")
        self.add_tasks()
        self.accept("escape", self.exit_task, [0])  # This is how we fire events inside this object

        self.add_inits()

    def reset(self):
        self.lp = None
        self.sp = None
        self.meh = None
        self.yaw_world_node = None
        self.pitch_world_node = None
        self.roll_world_node = None
        self.world_node = None
        self.counter = 0
        self.task_state = Task.cont
        self.light_dict = {}
        self.add_resets()

    def setup_text(self):
        title = OnscreenText(text="Simulator testbed",
                             style=1, fg=(1, 1, 1, 1), pos=(-0.1, 0.1), scale=.07,
                             parent=self.a2dBottomRight, align=TextNode.ARight)

    def stage_inits(self):
        self.world_node.setTransparency(TransparencyAttrib.MAlpha)
        self.axis_node = self.world_node.attachNewNode("Axis")
        self.grid_node = self.world_node.attachNewNode("Grid")
        self.axis_node.attachNewNode(self.lp.create_axis(4.0).node())
        self.grid_node.attachNewNode(self.lp.create_grid(size=10, color="trans_cyan").node())
        self.grid_node.attachNewNode(self.lp.create_grid(size=10, color="trans_magenta", plane="xz").node())
        self.grid_node.attachNewNode(self.lp.create_grid(size=10, color="trans_yellow", plane="yz").node())

        self.camera.setPos(0, 0, 0)
        self.camera.setHpr(0, 0, 0)
        self.world_translate_node.setPos(0, 10, 0)

    def add_directional_light(self, name:str, root_node:NodePath, target_node:NodePath, color:Tuple = (1,1,1,1)) -> NodePath:
        dlight = DirectionalLight(name)
        dlight.setColor(color)
        dlnp = root_node.attachNewNode(dlight)
        target_node.setLight(dlnp)
        self.light_dict[name] = dlnp
        return dlnp

    def clear_light(self, name:str):
        if name in self.light_dict:
            self.clear_light(name)
            del self.light_dict[name]

    def get_directional_light(self, name:str) -> Union[None, NodePath]:
        if name in self.light_dict:
            return self.light_dict[name]
        return None

    def add_graphic_inits(self):
        pass

    def add_inits(self):
        pass

    def add_resets(self):
        pass

    def add_setups(self, parent: NodePath):
        pass

    def add_tasks(self):
        pass

    def add_terminate(self):
        pass

    def exitFunc(self):
        print("Panda_main.exitFunc()")

    def exit_task(self, arg):
        self.task_state = Task.done
        self.taskMgr.remove("move_world_task")
        self.add_terminate()
        l = self.sfxManagerList
        sfxm:AudioManager
        for sfxm in l:
            sfxm.clear_cache()
            sfxm.shutdown()
        os._exit(0)

    # Define a procedure to move the world, rather than the camera.
    def move_world_task(self, task):
        try:
            if self.mouseWatcherNode.hasMouse():
                if self.meh.mouse1:
                    azimuth = self.mouseWatcherNode.getMouseX() * 2.0
                    elev = -self.mouseWatcherNode.getMouseY() * 2.0
                    yaw = self.world_yaw_node.getH()
                    yaw += azimuth
                    self.world_yaw_node.setH(yaw)

                    pitch = self.world_pitch_node.getP()
                    pitch += elev
                    self.world_pitch_node.setP(pitch)

                p = self.world_translate_node.getPos()
                p[1] += self.meh.mouse_wheel
                if self.meh.mouse3:
                    p[2] += self.mouseWatcherNode.getMouseY() / 2.0
                    p[0] += self.mouseWatcherNode.getMouseX() / 2.0
                self.world_translate_node.setPos(p)

        except AssertionError:
            pass
        return self.task_state


if __name__ == "__main__":
    pm = Pandas_main()
    pm.run()
