# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import math

from ipycanvas import Canvas
from ipylab import JupyterFrontEnd, Panel
from IPython.display import display
from ipywidgets import Box
from PIL import Image

from ..utils import Color
from .base import Backend

BLACK = Color(0)


class JupyterBackend(Canvas, Backend):
    """
    Widget and a Jyrobot backend.
    """

    def take_picture(self):
        """
        returns PIL.Image
        """
        # self.image_data gives a PNG bytes
        # self.get_image_data() gives numpy array
        array = self.get_image_data()
        picture = Image.fromarray(array, "RGBA")
        return picture

    def update_dimensions(self, width, height, scale):
        self._scale = scale
        self.width = round(width * self._scale)
        self.height = round(height * self._scale)
        self.resetScale()
        self.set_scale(self._scale)

    def set_scale(self, scale):
        self.scale(scale, scale)

    def do_command(self, command, *args):
        getattr(self, command)(*args)

    def watch(self, **kwargs):
        # where="inline"
        where = kwargs.pop("where", "inline")
        clear = kwargs.pop("clear", True)
        layout = kwargs
        if where in ["panel", "left", "right"]:
            app = JupyterFrontEnd()
            panel = Panel()

            if clear:
                for widget in list(app.shell.widgets.values()):
                    if hasattr(widget, "title") and widget.title.label.startswith(
                        "Jyrobot"
                    ):
                        widget.close()

            if where == "panel":
                # Close all Jyro widgets
                defaults = {"width": "100%", "height": "auto"}
                defaults.update(layout)
                box = Box()
                for keyword in defaults:
                    setattr(box.layout, keyword, defaults[keyword])
                    box.children = [self]

                panel.children = [box]
                panel.title.label = "Jyrobot Simulator"
                app.shell.add(panel, "main", {"mode": "split-right"})
            elif where == "left":
                panel.children = [self]
                panel.title.label = "Jyrobot Simulator"
                app.shell.add(panel, "left", {"rank": 10000})
                app.shell.expand_left()
            elif where == "right":
                panel.children = [self]
                panel.title.label = "Jyrobot Simulator"
                app.shell.add(panel, "right", {"rank": 0})
                app.shell.expand_right()
        else:  # "inline", or something else
            defaults = {"max_width": "600px"}
            defaults.update(layout)
            box = Box()
            for keyword in defaults:
                setattr(box.layout, keyword, defaults[keyword])
            box.children = [self]
            display(box)

    ## HIGH-LEVEL

    def clear(self):
        self.clear_rect(0, 0, self.width, self.height)

    def set_font(self, style):  # renamed
        self.font = style

    def text(self, t, x, y):
        self.fill_text(t, x, y)

    def lineWidth(self, width):
        self.line_width = width

    def strokeStyle(self, color, width):
        if color:
            self.set_stroke_style(color)
        else:
            self.set_stroke_style(BLACK)
        self.line_width = width

    def make_stroke(self):  # renamed
        self.stroke()

    def noStroke(self):
        self.set_stroke_style(BLACK)

    def set_fill(self, color):
        if color:
            self.set_fill_style(color)
        else:
            self.set_fill_style(BLACK)

    def noFill(self):
        self.set_fill_style(BLACK)

    def draw_line(self, x1, y1, x2, y2):
        self.beginShape()
        self.move_to(x1, y1)
        self.line_to(x2, y2)
        self.make_stroke()

    def pushMatrix(self):
        self.save()

    def popMatrix(self):
        self.restore()

    def resetScale(self):
        self.set_transform(1, 0, 0, 1, 0, 0)

    def beginShape(self):
        self.shape = False
        return self.begin_path()

    def endShape(self):
        self.close_path()
        self.fill()

    def vertex(self, x, y):
        if self.shape:
            self.line_to(x, y)
        else:
            self.move_to(x, y)
            self.shape = True

    def draw_rect(self, x, y, width, height):
        self.fill_rect(x, y, width, height)

    def draw_ellipse(self, x, y, radiusX, radiusY):
        self.begin_path()
        self.ellipse(x, y, radiusX, radiusY, 0, 0, math.pi * 2)
        self.fill()

    def draw_arc(self, x, y, width, height, startAngle, endAngle):
        prev_stroke_style = self.stroke_style
        #  Draw the pie:
        self.set_stroke_style(BLACK)
        self.begin_path()
        self.move_to(x, y)
        self.arc(x, y, width, startAngle, endAngle)
        self.line_to(x, y)
        self.fill()

        #  Draw the arc:
        self.stroke_style = prev_stroke_style
        self.begin_path()
        self.arc(x, y, width, startAngle, endAngle)
        self.make_stroke()
