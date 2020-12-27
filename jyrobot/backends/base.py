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

from ..utils import Color

BLACK = Color(0)
WHITE = Color(255)


class Backend:
    width = 0
    height = 0
    font = ""
    line_width = 1
    stroke_style = ""
    fill_style = ""

    def __init__(self, width, height, scale, **kwargs):
        self.width = width
        self.height = height
        self._scale = scale
        self.caching = False
        self.orig_caching = False
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        pass

    def update_watcher(self):
        # tell widget to update, if necessary
        pass

    def draw_watcher(self):
        # draw the widget, if necessary
        pass

    def reset_watcher(self):
        # reset the widget, if necessary
        pass

    def watch(self, *wheres, **kwargs):
        from ipylab import JupyterFrontEnd, Panel
        from IPython.display import display
        from ipywidgets import Box

        clear = kwargs.pop("clear", True)
        layout = kwargs
        if wheres == []:
            wheres = ["panel"]
        for where in wheres:
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
                        box.children = [self.get_widget()]

                    panel.children = [box]
                    panel.title.label = "Jyrobot Simulator"
                    app.shell.add(panel, "main", {"mode": "split-right"})
                elif where == "left":
                    panel.children = [self.get_widget()]
                    panel.title.label = "Jyrobot Simulator"
                    app.shell.add(panel, "left", {"rank": 10000})
                    app.shell.expand_left()
                elif where == "right":
                    panel.children = [self.get_widget()]
                    panel.title.label = "Jyrobot Simulator"
                    app.shell.add(panel, "right", {"rank": 0})
                    app.shell.expand_right()
            else:  # "inline", or something else
                defaults = {"max_width": "600px"}
                defaults.update(layout)
                box = Box()
                for keyword in defaults:
                    setattr(box.layout, keyword, defaults[keyword])
                box.children = [self.get_widget()]
                display(box)

    # jyrobot API:

    def is_async(self):
        # Does the backend take time to update the drawing?
        return False

    def get_dynamic_throttle(self, world):
        # If async, then return time needed to
        # draw world and return it
        return self.throttle_period

    # Canvas API

    def __enter__(self):
        self.orig_caching = self.caching
        self.caching = True

    def __exit__(self, *args, **kwargs):
        self.flush()
        if not self.orig_caching:
            self.caching = False

    def do_command(self, command, *args):
        getattr(self, command)(*args)

    def update_dimensions(self, width, height, scale):
        self._scale = scale
        self.width = round(width * self._scale)
        self.height = round(height * self._scale)
        self.resetScale()
        self.set_scale(self._scale)

    def set_scale(self, scale):
        self.scale(scale, scale)

    # Need to implement in subclasses:

    def get_widget(self):
        raise NotImplementedError("backend.get_widget")

    def flush(self):
        raise NotImplementedError("backend.flush")

    def take_picture(self):
        raise NotImplementedError("backend.take_picture")

    # HIGH-LEVEL Drawing API

    def draw_lines(self, points, stroke_style=None):
        if stroke_style is not None:
            self.set_stroke_style(stroke_style)
        for i in range(len(points)):
            if i < len(points) - 2:
                self.draw_line(
                    points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]
                )

    def set_stroke_style(self, color):
        self.stroke_style = color.to_hexcode()

    def set_fill_style(self, color):
        self.fill_style = color.to_hexcode()

    def clear(self):
        self.clear_rect(0, 0, self.width, self.height)

    def set_font(self, style):
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

    def make_stroke(self):
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

    # LOW-LEVEL SVG Drawing API
    # Need to implement in subclasses

    def arc(self, x, y, width, startAngle, endAngle):
        raise NotImplementedError("backend.arc")

    def get_image_data(self):
        raise NotImplementedError("backend.get_image_data")

    def clear_rect(self, x, y, width, height):
        raise NotImplementedError("backend.clear_rect")

    def fill_text(self, t, x, y):
        raise NotImplementedError("backend.fill_text")

    def fill_rect(self, x, y, width, height):
        raise NotImplementedError("backend.fill_rect")

    def fill(self):
        raise NotImplementedError("backend.fill")

    def stroke(self):
        raise NotImplementedError("backend.stroke")

    def move_to(self, x, y):
        raise NotImplementedError("backend.move_to")

    def line_to(self, x, y):
        raise NotImplementedError("backend.line_to")

    def save(self):
        raise NotImplementedError("backend.save")

    def restore(self):
        raise NotImplementedError("backend.restore")

    def translate(self, x, y):
        raise NotImplementedError("backend.translate")

    def scale(self, xscale, yscale):
        raise NotImplementedError("backend.scale")

    def set_transform(self, x, y, z, a, b, c):
        raise NotImplementedError("backend.set_transform")

    def rotate(self, angle):
        raise NotImplementedError("backend.rotate")

    def begin_path(self):
        raise NotImplementedError("backend.begin_path")

    def close_path(self):
        raise NotImplementedError("backend.close_path")

    def ellipse(self, x, y, radiusX, radiusY, a, b, angle):
        raise NotImplementedError("backend.ellipse")

    def put_image_data(self, scaled, x, y):
        raise NotImplementedError("backend.put_image_data")

    def create_image_data(sefl, width, height):
        raise NotImplementedError("backend.create_image_data")
