# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from ..config import get_backend


def make_backend(width, height, scale):
    BACKEND, ARGS = get_backend()

    if BACKEND == "canvas":
        from .canvas import CanvasBackend

        return CanvasBackend(
            width=round(width * scale),
            height=round(height * scale),
            sync_image_data=True,
            **ARGS
        )
    elif BACKEND == "svg":
        from .svg import SVGBackend

        return SVGBackend(width, height, scale, **ARGS)
    elif BACKEND == "pil":
        from .pil import PILBackend

        return PILBackend(width, height, scale, **ARGS)
    elif BACKEND == "debug":
        from .debug import DebugBackend

        return DebugBackend(width, height, scale, **ARGS)
    else:
        raise ValueError("unknown backend type: %r" % BACKEND)
