# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from ._version import __version__  # noqa: F401
from .config import setup_backend, switch_backend  # noqa: F401
from .devices import Camera, RangeSensor  # noqa: F401
from .robot import Robot, Scribbler  # noqa: F401
from .utils import load_world  # noqa: F401
from .world import World  # noqa: F401

setup_backend()  # checks os.environ
