# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import numpy as np
from ipycanvas import Canvas
from ipylab import JupyterFrontEnd, Panel
from IPython.display import display
from ipywidgets import Box
from PIL import Image

from .base import Backend


def get_args(where="panel", clear=True):
    return (where, clear)


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

    def watch(self, *args, **kwargs):
        layout = kwargs.pop("layout", {})
        where, clear = get_args(*args, **kwargs)
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

    # High Level-API overloads:

    def draw_lines(self, points, stroke_style=None):
        if stroke_style:
            self.strokeStyle(stroke_style, 1)
        data = np.array(points)
        self.stroke_lines(data)
