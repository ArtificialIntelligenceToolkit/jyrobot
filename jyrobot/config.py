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

HERE = os.path.abspath(os.path.dirname(__file__))
PATHS = ["./", os.path.join(HERE, "worlds")]

BACKEND = "pil"  # or any valid backends
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
