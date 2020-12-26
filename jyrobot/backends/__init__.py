# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import ast
import os

BACKEND = "pil" # or any valid backends
ARGS = {}
VALID_BACKENDS = ["canvas", "svg", "debug", "pil"]


def setup_backend():
    global BACKEND, ARGS

    BACKEND = os.environ.get("JYROBOT_BACKEND", BACKEND)
    if ":" in BACKEND:
        BACKEND, ARGS = BACKEND.split(":", 1)
        ARGS = ast.literal_eval(ARGS)
    else:
        ARGS = {}


def switch_backend(backend=None, **kwargs):
    global BACKEND, ARGS

    if backend is None:
        return VALID_BACKENDS
    elif backend in VALID_BACKENDS:
        BACKEND = backend
        ARGS = kwargs
    else:
        raise ValueError("unknown backend type: %r" % backend)


def make_backend(width, height, scale):
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
