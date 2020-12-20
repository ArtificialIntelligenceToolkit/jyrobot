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
from random import random  # noqa: F401

from ._version import __version__  # noqa: F401
from .backends import switch_backend  # noqa: F401
from .devices import Camera, RangeSensor  # noqa: F401
from .robot import Robot, Scribbler  # noqa: F401
from .world import World

HERE = os.path.abspath(os.path.dirname(__file__))

PATHS = ["./", os.path.join(HERE, "worlds")]


def load(filename):
    if not filename.endswith(".json"):
        filename += ".json"
    for path in PATHS:
        path_filename = os.path.join(path, filename)
        if os.path.exists(path_filename):
            with open(path_filename) as fp:
                contents = fp.read()
                config = json.loads(contents)
                config["filename"] = path_filename
                world = World(**config)
                return world
    print("No such world found: %r" % filename)
    return None
