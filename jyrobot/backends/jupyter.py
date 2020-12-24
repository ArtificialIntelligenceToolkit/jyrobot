# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import numpy as np
from ipycanvas import Canvas

from .base import Backend


class JupyterBackend(Canvas, Backend):
    """
    Canvas Widget and a Jyrobot backend.
    """

    # jyrobot API:

    def is_async(self):
        # Does the backend take time to update the drawing?
        return True

    def get_dynamic_throttle(self, world):
        # A proxy to figure out how much to throttle
        return world.complexity * 0.005

    def take_picture(self):
        """
        returns PIL.Image
        """
        from PIL import Image

        # self.image_data gives a PNG bytes
        # self.get_image_data() gives numpy array
        array = self.get_image_data()
        picture = Image.fromarray(array, "RGBA")
        return picture

    def get_widget(self):
        return self

    # High Level-API overloads:

    def draw_lines(self, points, stroke_style=None):
        if stroke_style:
            self.strokeStyle(stroke_style, 1)
        data = np.array(points)
        self.stroke_lines(data)
