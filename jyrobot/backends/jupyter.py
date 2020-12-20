# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from ipycanvas import Canvas

from .base import Backend


class JupyterBackend(Canvas, Backend):
    """
    Widget and a Jyrobot backend.
    """
