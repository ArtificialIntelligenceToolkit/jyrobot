# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import os

BACKEND = os.environ.get("JYROBOT_BACKEND", "jupyter")

VALID_BACKENDS = ["jupyter", "svg", "debug"]


def switch_backend(backend=None):
    global BACKEND

    if backend is None:
        return VALID_BACKENDS
    elif backend in VALID_BACKENDS:
        BACKEND = backend
    else:
        raise ValueError("unknown backend type: %r" % backend)


def make_backend(width, height, scale):
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

        return SVGBackend(width, height, scale)
    elif BACKEND == "debug":
        from .debug import DebugBackend

        return DebugBackend(width, height, scale)
    else:
        raise ValueError("unknown backend type: %r" % BACKEND)
