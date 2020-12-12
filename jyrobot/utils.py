import io

from PIL import Image as Image

class Color():
    def __init__(self, red, green=None, blue=None, alpha=None):
        self.red = red
        if (green != None):
            self.green = green
        else:
            self.green = red
        if (blue != None):
            self.blue = blue
        else:
            self.blue = red
        if (alpha != None):
            self.alpha = alpha
        else:
            self.alpha = 255

    def __str__(self):
        return "#%02X%02X%02X%02X" % (self.red, self.green, self.blue, self.alpha)

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

class Picture():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = Image.new('RGBA', (self.width, self.height))
        self.pixels = self.image.load()

    def set(self, x, y, color):
        self.pixels[x, y] = (int(color.red), int(color.green), int(color.blue), int(color.alpha))

    def get(self, x, y):
        return self.pixels[x, y]

    def to_bytes(self, format="png"):
        with io.BytesIO() as fp:
            self.image.save(fp, format=format)
            data = fp.getvalue()
        return data

    def _repr_png_(self):
        return self.to_bytes()
