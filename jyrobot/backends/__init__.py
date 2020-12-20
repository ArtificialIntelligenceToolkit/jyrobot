# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

BACKEND = "jupyter"


def switch_backend(backend):
    global BACKEND
    BACKEND = backend


def make_backend(width, height, scale, world_width, world_height):
    if BACKEND == "jupyter":
        from ipywidgets import Layout
        from .jupyter import JupyterBackend

        layout = Layout(width="100%", height="auto")
        return JupyterBackend(
            width=round(width * scale),
            height=round(height * scale),
            sync_image_data=True,
            layout=layout,
        )
    elif BACKEND == "svg":
        from .svg import SVGBackend

        return SVGBackend(width, height, world_width, world_height)
    elif BACKEND == "debug":
        from .debug import DebugBackend

        return DebugBackend(width, height)
    elif BACKEND == "dummy":
        from .base import Backend

        return Backend(width, height)
