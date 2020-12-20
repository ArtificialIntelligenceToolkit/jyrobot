# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************


from .base import Backend


class DebugBackend(Backend):
    def arc(self, x, y, width, startAngle, endAngle):
        print("arc(%r,%r,%r,%r,%r)" % (x, y, width, startAngle, endAngle))

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
