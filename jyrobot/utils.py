# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from ipywidgets import Layout

# from ipylab import JupyterFrontEnd

# def remove_canvases():
#     app = JupyterFrontEnd()
#     for widget in app.shell.widgets.values():
#         print(widget)
#         if hasattr(widget, "title") and title.startswith("Jyrobot"):
#             widget.close()


def get_canvas(config, width, height, scale=1.0, gc=None):
    from .canvas import Canvas

    config["width"] = round(width * scale)
    config["height"] = round(height * scale)

    canvas = Canvas(config["width"], config["height"], gc)
    if gc is None:
        canvas.gc.scale(scale, scale)
    canvas.gc.layout = Layout(width="%spx" % config["width"])
    return canvas


class Color:
    def __init__(self, red, green=None, blue=None, alpha=None):
        self.red = red
        if green is not None:
            self.green = green
        else:
            self.green = red
        if blue is not None:
            self.blue = blue
        else:
            self.blue = red
        if alpha is not None:
            self.alpha = alpha
        else:
            self.alpha = 255

    def __str__(self):
        return "#%02X%02X%02X%02X" % self.to_tuple()

    def to_tuple(self):
        return (int(self.red), int(self.green), int(self.blue), int(self.alpha))


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point(%s,%s)" % (self.x, self.y)


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        return "Line(%s,%s)" % (self.x, self.y)
