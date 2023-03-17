import random

from panda3d.core import LVecBase4f


class DefinedColors():
    red = None
    green = None
    blue = None
    cyan = None
    magenta = None
    yellow = None
    white = None
    light_gray = None
    dark_gray = None
    gray = None
    black = None

    def __init__(self):
        self.create_colors()

    def create_colors(self):
        self.red = LVecBase4f(1, 0, 0, 1)
        self.trans_red = LVecBase4f(1, 0, 0, 0.3)
        self.dark_red = LVecBase4f(0.5, 0, 0, 1)
        self.light_red = LVecBase4f(1, 0.5, 0.5, 1)
        self.venetian_red = LVecBase4f(0.7843, 0.0314, 0.0824, 1) # #c80815 is comprised of 78.43% red, 3.14% green and 8.24% blue.
        self.test_red = LVecBase4f(0.6275, 0.024, 0.0667, 1) # #a00611 is comprised of 62.75% red, 2.35% green and 6.67% blue - dark_venetianred
        self.green = LVecBase4f(0, 1, 0, 1)
        self.trans_green = LVecBase4f(0, 1, 0, 0.3)
        self.dark_green = LVecBase4f(0, 0.5, 0, 1) #0.39% red, 19.61% green and 12.55% blue
        self.brit_racegreen = LVecBase4f(0, 0.258, 0.145, 1) # #004225 is comprised of 0% red, 25.88% green and 14.51% blue.
        self.royal_green = LVecBase4f(0.075, 0.384, 0.0275, 1) # #136207 is comprised of 7.45% red, 38.43% green and 2.75% blue
        self.light_green = LVecBase4f(0.5, 1, 0.5, 1)
        self.blue = LVecBase4f(0, 0, 1, 1)
        self.cobalt_blue = LVecBase4f(0.18, 0.1765, 0.5333, 1) # #2e2d88 is comprised of 18.04% red, 17.65% green and 53.33% blue
        self.metallic_blue = LVecBase4f(0.1961, 0.3216, 0.4824, 1) # #32527b is comprised of 19.61% red, 32.16% green and 48.24% blue
        self.trans_blue = LVecBase4f(0, 0, 1, 0.3)
        self.dark_blue = LVecBase4f(0, 0, 0.5, 1)
        self.light_blue = LVecBase4f(0.5, 0.5, 1, 1)
        self.cyan = LVecBase4f(0, 1, 1, 1)
        self.trans_cyan = LVecBase4f(0, 1, 1, 0.3)
        self.light_cyan = LVecBase4f(0.5, 1, 1, 1)
        self.dark_cyan = LVecBase4f(0, 0.5, 0.5, 1)
        self.magenta = LVecBase4f(1, 0, 1, 1)
        self.trans_magenta = LVecBase4f(1, 0, 1, 0.3)
        self.light_magenta = LVecBase4f(1, 0.5, 1, 1)
        self.dark_magenta = LVecBase4f(0.5, 0, 0.5, 1)
        self.yellow = LVecBase4f(1, 1, 0, 1)
        self.trans_yellow = LVecBase4f(1, 1, 0, 0.3)
        self.light_yellow = LVecBase4f(1, 1, 0.5, 1)
        self.dark_yellow = LVecBase4f(0.5, 0.5, 0, 1)
        self.white = LVecBase4f(1, 1, 1, 1)
        self.light_gray = LVecBase4f(0.7, 0.7, 0.7, 1)
        self.dark_gray = LVecBase4f(0.3, 0.3, 0.3, 1)
        self.aluminum_gray = LVecBase4f(0.41, 0.40, 0.40, 1)
        self.audi_titanium_grey = LVecBase4f(0.49, 0.5098, 0.5133, 1) # 50.98% red, 52.94% green and 53.33% blue.
        self.trans_gray = LVecBase4f(0.6, 0.6, 0.6, 0.1)
        self.gray = LVecBase4f(0.5, 0.5, 0.5, 1)
        self.black = LVecBase4f(0.0, 0.0, 0.0, 1)
        self.orange = LVecBase4f(1, 0.5, 0.0, 1)
        self.brave_orange = LVecBase4f(1, 0.383, 0.109, 1) # #ff631c is comprised of 100% red, 38.82% green and 10.98% blue
        self.maximum_orange = LVecBase4f(1, 0.357, 0, 1) # #ff5b00 is comprised of 100% red, 35.69% green and 0% blue.
        self.metallic_orange = LVecBase4f(0.855, 0.408, 0.0588, 1) # #da680f is comprised of 85.49% red, 40.78% green and 5.88% blue
        self.titanium = LVecBase4f(0.385, 0.393, 0.436, 1) # ##6c6b67 is comprised of 42.35% red, 41.96% green and 40.39% blue.
        self.fordtitanium = LVecBase4f(0.345, 0.353, 0.396, 1) # #585a65 is comprised of 34.51% red, 35.29% green and 39.61% blue
        self.rocket_metallic = LVecBase4f(0.5412, 0.4918, 0.502, 1) # #8a7f80 is comprised of 54.12% red, 49.8% green and 50.2% blue.
        self.chrome_aluminum = LVecBase4f(0.522, 0.525, 0.549, 1) # #85868c is comprised of 52.16% red, 52.55% green and 54.9% blue
        self.silver_foil = LVecBase4f(0.6863, 0.6941, 0.6824, 1) # #afb1ae is comprised of 68.63% red, 69.41% green and 68.24% blue.
        self.quick_silver = LVecBase4f(0.651, 0.651, 0.651, 1) # #a6a6a6 is comprised of 65.1% red, 65.1% green and 65.1% blue.
        self.dark_silver = LVecBase4f(0.4431, 0.439, 0.4314, 1) # #71706e is comprised of 44.31% red, 43.92% green and 43.14% blue.
        self.dark_silvermetallic = LVecBase4f(0.5294, 0.5255, 0.549, 1) # #87868c is comprised of 52.94% red, 52.55% green and 54.9% blue.
        self.roman_silver = LVecBase4f(0.513, 0.5373, 0.5882, 1) # #838996 is comprised of 51.37% red, 53.73% green and 58.82% blue.
        self.dark_romansilver = LVecBase4f(0.404, 0.4275, 0.4784, 1) # #676d7a is comprised of 40.39% red, 42.75% green and 47.84% blue.
        self.imperial_purple = LVecBase4f(0.376, 0.184, 0.419, 1) # #602f6b is comprised of 37.65% red, 18.43% green and 41.96% blue

    def get_color(self, name: str):
        n = name.lower()
        return {
            'red': self.red,
            'trans_red': self.trans_red,
            'dark_red': self.dark_red,
            'light_red': self.light_red,
            'venetian_red': self.venetian_red,
            'test_red': self.test_red,
            'green': self.green,
            'trans_green': self.trans_green,
            'dark_green': self.dark_green,
            'royal_green': self.royal_green,
            'light_green': self.light_green,
            'blue': self.blue,
            'cobalt_blue': self.cobalt_blue,
            'metallic_blue': self.metallic_blue,
            'trans_blue': self.trans_blue,
            'dark_blue': self.dark_blue,
            'light_blue': self.light_blue,
            'cyan': self.cyan,
            'trans_cyan': self.trans_cyan,
            'dark_cyan': self.dark_cyan,
            'light_cyan': self.light_cyan,
            'magenta': self.magenta,
            'trans_magenta': self.trans_magenta,
            'light_magenta': self.light_magenta,
            'dark_magenta': self.dark_magenta,
            'yellow': self.yellow,
            'trans_yellow': self.trans_yellow,
            'light_yellow': self.light_yellow,
            'dark_yellow': self.dark_yellow,
            'white': self.white,
            'light_gray': self.light_gray,
            'light_grey': self.light_gray,
            'dark_gray': self.dark_gray,
            'dark_grey': self.dark_gray,
            'aluminum_gray': self.aluminum_gray,
            'audi_titanium_grey': self.audi_titanium_grey,
            'audi_titanium_gray': self.audi_titanium_grey,
            'trans_grey': self.trans_gray,
            'trans_gray': self.trans_gray,
            'gray': self.gray,
            'grey': self.gray,
            'black': self.black,
            'orange': self.orange,
            'brave_orange': self.brave_orange,
            'maximum_orange': self.maximum_orange,
            'metallic_orange': self.metallic_orange,
            'titanium': self.titanium,
            'fordtitanium': self.fordtitanium,
            'rocket_metallic': self.rocket_metallic,
            'chrome_aluminum': self.chrome_aluminum,
            'silver_foil': self.silver_foil,
            'quick_silver': self.quick_silver,
            'dark_silver': self.dark_silver,
            'dark_silvermetallic': self.dark_silvermetallic,
            'roman_silver': self.roman_silver,
            'dark_romansilver': self.dark_romansilver,
            'british_racegreen': self.brit_racegreen,
            'imperial_purple': self.imperial_purple,
        }.get(name, self.black)

    def jiggle_color(self, c: LVecBase4f, scalar: float = 0.3) -> LVecBase4f:
        c2 = LVecBase4f(c)
        for i in range(3):
            val = c2[i]
            if val == 0:
                val += random.random() * scalar
            elif val == 1.0:
                val -= random.random() * scalar
            else:
                val += (random.random() - 0.5) * scalar
            val = max(0, val)
            val = min(1.0, val)
            c2[i] = val
        return c2
