# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import json
import os

from ipylab import JupyterFrontEnd, Panel
from ipywidgets import Layout

from ._version import __version__  # noqa: F401
from .canvas import Canvas
from .world import World

HERE = os.path.abspath(os.path.dirname(__file__))

PATHS = ["./", os.path.join(HERE, "worlds")]


def get_canvas(config, width, height, scale=1.0):
    config["width"] = round(width * scale)
    config["height"] = round(height * scale)

    canvas = Canvas(config["width"], config["height"])
    canvas.gc.scale(scale, scale)
    canvas.gc.layout = Layout(width="%spx" % config["width"])
    return canvas


def load(filename):
    filename += ".json"
    for path in PATHS:
        path_filename = os.path.join(path, filename)
        if os.path.exists(path_filename):
            with open(path_filename) as fp:
                contents = fp.read()
                config = json.loads(contents)
                canvas = get_canvas(config, 500, 250, 1.75)

                app = JupyterFrontEnd()

                panel = None
                for widget in app.shell.widgets.values():
                    if (
                        hasattr(widget, "title")
                        and widget.title.label == "Jyrobot Simulator"
                    ):
                        # panel = widget
                        break

                if panel is None:
                    panel = Panel()
                    panel.children = [canvas.gc]
                    panel.title.label = "Jyrobot Simulator"
                    app.shell.add(panel, "main", {"mode": "split-right"})
                else:
                    panel.children = [canvas.gc]
                world = World(config, canvas)
                world.update()
                return world
    return None
