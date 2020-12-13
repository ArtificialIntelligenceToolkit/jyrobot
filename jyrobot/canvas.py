# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import math

from ipycanvas import Canvas as ICanvas


class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.gc = ICanvas(width=self.width, height=self.height)
        self.shape = False  # in the middle of a shape?

    def clear(self):
        self.gc.clear_rect(0, 0, self.width, self.height)

    def font(self, style):
        self.gc.font = style

    def text(self, t, x, y):
        self.gc.fill_text(t, x, y)

    def lineWidth(self, width):
        self.gc.line_width = width

    def strokeStyle(self, color, width):
        if color:
            self.gc.stroke_style = str(color)
        else:
            self.gc.stroke_style = "#000000"
        self.gc.line_width = width

    def stroke(self):
        self.gc.stroke()

    def noStroke(self):
        self.gc.stroke_style = "#000000"

    def fill(self, color):
        if color:
            self.gc.fill_style = str(color)
        else:
            self.gc.fill_style = "#000000"

    def noFill(self):
        self.gc.fill_style = "#000000"

    def line(self, x1, y1, x2, y2):
        self.beginShape()
        self.gc.move_to(x1, y1)
        self.gc.line_to(x2, y2)
        self.gc.stroke()

    def pushMatrix(self):
        self.gc.save()

    def popMatrix(self):
        self.gc.restore()

    def translate(self, x, y):
        self.gc.translate(x, y)

    def scale(self, x, y):
        self.gc.scale(x, y)

    def resetScale(self):
        self.gc.set_transform(1, 0, 0, 1, 0, 0)

    def rotate(self, angle):
        self.gc.rotate(angle)

    def beginShape(self):
        self.shape = False
        return self.gc.begin_path()

    def endShape(self):
        self.gc.close_path()
        self.gc.fill()

    def vertex(self, x, y):
        if self.shape:
            self.gc.line_to(x, y)
        else:
            self.gc.move_to(x, y)
            self.shape = True

    def rect(self, x, y, width, height):
        self.gc.fill_rect(x, y, width, height)

    def ellipse(self, x, y, radiusX, radiusY):
        self.gc.begin_path()
        self.gc.ellipse(x, y, radiusX, radiusY, 0, 0, math.pi * 2)
        self.gc.fill()

    def picture(self, pic, x, y, scale=1.0):
        scaled = self.scaleImageData(pic, scale)
        self.gc.put_image_data(scaled, x, y)

    def scaleImageData(self, pic, scale):
        scaled = self.gc.create_image_data(pic.width * scale, pic.height * scale)
        subLine = self.gc.create_image_data(scale, 1).data
        for row in range(pic.height):
            for col in range(pic.width):
                sourcePixel = pic.get(col, row)
                for x in range(scale):
                    subLine.set(sourcePixel, x * 4)
                for y in range(scale):
                    destRow = row * scale + y
                    destCol = col * scale
                    scaled.data.set(subLine, (destRow * scaled.width + destCol) * 4)
        return scaled

    def arc(self, x, y, width, height, startAngle, endAngle):
        #  Draw the pie:
        self.gc.stroke_style = "#000000"
        self.gc.begin_path()
        self.gc.move_to(x, y)
        self.gc.arc(x, y, width, startAngle, endAngle)
        self.gc.line_to(x, y)
        self.gc.fill()

        #  Draw the arc:
        self.gc.stroke_style = "#000000"
        self.gc.begin_path()
        self.gc.arc(x, y, width, startAngle, endAngle)
        self.gc.stroke()
