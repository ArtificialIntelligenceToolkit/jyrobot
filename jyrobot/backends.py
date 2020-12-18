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
    line_width = 0
    stroke_style = ""
    fill_style = ""
    
    def __init__(self, width, height, sync_image_data=True, layout=None):
        self.width = width
        self.height = height
        self.caching = False

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def flush(self):
        pass

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
    

class DebugBackend(Backend):
    width = 0
    height = 0
    font = ""
    line_width = 0
    stroke_style = ""
    fill_style = ""
    
    def arc(self, x, y, width, startAngle, endAngle):
        print("arc(", x, y, width, startAngle, endAngle, ")")
    def get_image_data(self):
        print("get_image_data()")
    def clear_rect(self, x, y, width, height):
        print("clear_rect(", x, y, width, height, ")")
    def fill_text(self, t, x, y):
        print("fill_text(", t, x, y, ")")
    def fill_rect(self, x, y, width, height):
        print("fill_rect(", x, y, width, height, ")")
    def fill(self):
        print("fill()")
    def stroke(self):
        print("stroke()")
    def move_to(self, x, y):
        print("move_to(", x, y, ")")
    def line_to(self, x, y):
        print("line_to(", x, y, ")")
    def save(self):
        print("save()")
    def restore(self):
        print("restore()")
    def translate(self, x, y):
        print("translate(", x, y, ")")
    def scale(self, xscale, yscale):
        print("scale(", xscale, yscale, ")")
    def set_transform(self, x, y, z, a, b, c):
        print("set_transform(", x, y, z, a, b, c, ")")
    def rotate(self, angle):
        print("rotate(", angle, ")")
    def begin_path(self):
        print("begin_path()")
    def close_path(self):
        print("close_path()")
    def ellipse(self, x, y, radiusX, radiusY, a, b, angle):
        print("ellipse(", x, y, radiusX, radiusY, a, b, angle, ")")
    def put_image_data(self, scaled, x, y):
        print("put_image_data(", scaled, x, y, ")")
    def create_image_data(self, width, height):
        print("create_image_data(", width, height, ")")
    

