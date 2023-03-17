import sys

from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import TextNode, TransparencyAttrib, WindowProperties

from gpt2agents.Panda3D.LinePrimitives import LinePrimitives
from gpt2agents.Panda3D.MouseEventHandler import MouseEventHandler
from gpt2agents.Panda3D.ShapePrimitives import ShapePrimitives


class ExercisePrimitives(ShowBase):
    lp = None
    sp = None
    meh = None
    yaw_world_node = None
    pitch_world_node = None
    roll_world_node = None
    world_node = None
    counter = 0

    def __init__(self):
        ShowBase.__init__(self)

        props = WindowProperties()
        props.setTitle('My window')
        self.win.requestProperties(props)

        self.setBackgroundColor(0.25, 0.25, 0.25)

        self.lp = LinePrimitives()
        self.sp = ShapePrimitives()
        self.meh = MouseEventHandler(.01)

        # Reparent the model to render.
        # self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        # self.scene.setScale(1.0, 1.0, 1.0)
        # self.scene.setPos(0, 0, 0)

        self.disableMouse()

        self.setup_text()

        self.world_translate_node = self.render.attachNewNode("world_translate")

        self.world_pitch_node = self.world_translate_node.attachNewNode("world_pitch_node")
        self.world_yaw_node = self.world_pitch_node.attachNewNode("world_yaw_node")

        self.world_roll_node = self.world_yaw_node.attachNewNode("world_roll_node")
        self.world_node = self.world_roll_node.attachNewNode("world")

        self.world_node.setTransparency(TransparencyAttrib.MAlpha)
        self.world_node.attachNewNode(self.lp.create_axis(5).node())
        self.world_node.attachNewNode(self.lp.create_grid(size=2, color="trans_cyan").node())
        self.world_node.attachNewNode(self.lp.create_grid(size=2, color="trans_magenta", plane="xz").node())
        self.world_node.attachNewNode(self.lp.create_grid(size=2, color="trans_yellow", plane="yz").node())

        node = self.sp.create_cylinder(radius=0.3, zmax=0.3, zmin=0.2, cname="red")
        self.world_node.attachNewNode(node)
        cap_node = self.sp.create_disk(zpos=0.3, radius=0.3, cname="light_gray")
        self.world_node.attachNewNode(cap_node)

        node = self.sp.create_conic(rzmin=0.4, rzmax=0.1, zmin=0, zmax=0.2, cname="blue")
        self.world_node.attachNewNode(node)

        node = self.sp.create_sphere(radius=0.2)
        nodepath = self.world_node.attachNewNode(node)
        nodepath.setPos(0, 0, .5)

        self.camera.setPos(0, 0, 0)
        self.camera.setHpr(0, 0, 0)
        self.world_translate_node.setPos(0, 10, 0)

        # Add the move_world_task procedure to the task manager.
        self.taskMgr.add(self.update_actions_task, "update_actions_task")
        self.taskMgr.add(self.move_world_task, "move_world_task")
        self.taskMgr.add(self.update_text_task, "update_text_task")

        self.accept("escape", sys.exit, [0])  # This is how we fire events inside this object

    def setup_text(self):
        title = OnscreenText(text="Procedural Geometry Demo",
                             style=1, fg=(1, 1, 1, 1), pos=(-0.1, 0.1), scale=.07,
                             parent=self.a2dBottomRight, align=TextNode.ARight)

        self.updating_text = OnscreenText(text="This number updates: 000",
                                          style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.1),
                                          align=TextNode.ALeft, scale=.05,
                                          parent=self.a2dTopLeft)

    def update_actions_task(self, task):
        self.counter += 0.1
        return Task.cont

    def update_text_task(self, task):
        s = "This number updates: {:.1f}".format(self.counter)
        self.updating_text.textNode.setText(s)

        return Task.cont

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
                    p[1] += self.mouseWatcherNode.getMouseY() / 2.0
                self.world_translate_node.setPos(p)

        except AssertionError:
            pass
        return Task.cont


if __name__ == "__main__":
    ep = ExercisePrimitives()
    ep.run()
