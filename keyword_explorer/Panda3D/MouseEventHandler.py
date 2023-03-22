from direct.showbase import DirectObject


class MouseEventHandler(DirectObject.DirectObject):
    mouse1 = False
    mouse2 = False
    mouse3 = False
    mouse_wheel = 0
    wheel_step = 0.5

    def __init__(self, wheel_step: float = 0, wheel_start: float = 0):
        if wheel_step != 0:
            self.wheel_step = wheel_step

        self.mouse_wheel = wheel_start

        self.accept('mouse1', self.mouse1_down)
        self.accept('mouse1-up', self.mouse1_up)
        self.accept('mouse2', self.mouse2_down)
        self.accept('mouse2-up', self.mouse2_up)
        self.accept('mouse3', self.mouse3_down)
        self.accept('mouse3-up', self.mouse3_up)
        self.accept('wheel_up', self.wheel_up)
        self.accept('wheel_down', self.wheel_down)

    def mouse1_down(self):
        self.mouse1 = True

    def mouse1_up(self):
        self.mouse1 = False

    def mouse2_down(self):
        self.mouse2 = True

    def mouse2_up(self):
        self.mouse2 = False

    def mouse3_down(self):
        self.mouse3 = True

    def mouse3_up(self):
        self.mouse3 = False

    def wheel_down(self):
        self.mouse_wheel -= self.wheel_step
        # print("+mouse_wheel = {}".format(self.mouse_wheel))

    def wheel_up(self):
        self.mouse_wheel += self.wheel_step
        # print("-mouse_wheel = {}".format(self.mouse_wheel))
