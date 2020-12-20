# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************


class Backend:
    width = 0
    height = 0
    font = ""
    line_width = 1
    stroke_style = ""
    fill_style = ""

    def __init__(self, width, height, scale):
        self.width = width
        self.height = height
        self.scale = scale
        self.caching = False
        self.orig_caching = False

    # Canvas API

    def __enter__(self):
        self.orig_caching = self.caching
        self.caching = True

    def __exit__(self, *args, **kwargs):
        self.flush()
        if not self.orig_caching:
            self.caching = False

    def flush(self):
        pass

    # HIGH-LEVEL Drawing API

    def set_stroke_style(self, color):
        self.stroke_style = color.to_hexcode()

    def set_fill_style(self, color):
        self.fill_style = color.to_hexcode()

    # LOW-LEVEL SVG Drawing API

    def arc(self, x, y, width, startAngle, endAngle):
        pass

    def get_image_data(self):
        pass

    def clear_rect(self, x, y, width, height):
        pass

    def fill_text(self, t, x, y):
        pass

    def fill_rect(self, x, y, width, height):
        pass

    def fill(self):
        pass

    def stroke(self):
        pass

    def move_to(self, x, y):
        pass

    def line_to(self, x, y):
        pass

    def save(self):
        pass

    def restore(self):
        pass

    def translate(self, x, y):
        pass

    def scale(self, xscale, yscale):
        pass

    def set_transform(self, x, y, z, a, b, c):
        pass

    def rotate(self, angle):
        pass

    def begin_path(self):
        pass

    def close_path(self):
        pass

    def ellipse(self, x, y, radiusX, radiusY, a, b, angle):
        pass

    def put_image_data(self, scaled, x, y):
        pass

    def create_image_data(sefl, width, height):
        pass
