# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import glob
import json
import os

from ._version import __version__  # noqa: F401
from .backends import switch_backend  # noqa: F401
from .devices import Camera, RangeSensor  # noqa: F401
from .robot import Robot, Scribbler  # noqa: F401
from .world import World

HERE = os.path.abspath(os.path.dirname(__file__))

PATHS = ["./", os.path.join(HERE, "worlds")]


def load(filename=None):
    if filename is None:
        print("Searching for jyrobot config files...")
        for path in PATHS:
            files = sorted(glob.glob(os.path.join(path, "*.json")))
            print("Directory:", path)
            if len(files) > 0:
                for filename in files:
                    basename = os.path.splitext(os.path.basename(filename))[0]
                    print("    %r" % basename)
            else:
                print("    no files found")
    else:
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
