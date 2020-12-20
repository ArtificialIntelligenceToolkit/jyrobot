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

from svgwrite import Drawing

from .base import Backend


class SVGBackend(Backend):
    def __init__(self, width, height, world_width, world_height):
        super().__init__(width, height)
        self.world_width = world_width
        self.world_height = world_height
        self.stack = []
        self.points = []
        self.initialize()

    def initialize(self):
        self.stack.clear()
        dwg = Drawing("canvas.svg", (self.world_width, self.world_height))
        dwg.viewbox(0, 0, self.world_width, self.world_height)
        self.stack.append(dwg)

    def set_stroke_style(self, color):
        self.stroke_style = color.rgb()

    def set_fill_style(self, color):
        self.fill_style = color.rgb()

    def get_style(self, *items):
        map = {
            "fill": ("fill:%s" % self.fill_style) if self.fill_style else None,
            "stroke-width": "stroke-width:%s" % self.line_width,
            "stroke": ("stroke:%s" % self.stroke_style) if self.stroke_style else None,
        }
        styles = []
        for item in items:
            styles.append(map[item])
        style = ";".join(styles)
        return style

    def arc(self, x, y, radius, startAngle, endAngle):
        def polarToCartesian(centerX, centerY, radius, angleInRadians):
            return [
                centerX + (radius * math.cos(angleInRadians)),
                centerY + (radius * math.sin(angleInRadians)),
            ]

        start = polarToCartesian(x, y, radius, endAngle)
        end = polarToCartesian(x, y, radius, startAngle)

        path = ["M", start[0], start[1], "A", radius, radius, 0, 0, 0, end[0], end[1]]
        path = [str(item) for item in path]
        d = " ".join(path)
        dwg = self.stack[-1]
        style = self.get_style("fill", "stroke", "stroke-width")
        dwg.add(self.stack[0].path(d=d, style=style))

    def get_image_data(self):
        pass

    def clear_rect(self, x, y, width, height):
        self.initialize()

    def fill_text(self, text, x, y):
        style = self.get_style("fill")
        dwg = self.stack[-1]
        dwg.add(self.stack[0].text(text=text, insert=(x, y), style=style))

    def fill_rect(self, x, y, width, height):
        style = self.get_style("fill")
        self.stack[-1].add(
            self.stack[0].rect(insert=(x, y), size=(width, height), style=style)
        )

    def fill(self):
        if len(self.points) >= 2:
            style = self.get_style("fill")
            dwg = self.stack[-1]
            dwg.add(self.stack[0].polygon(points=self.points, style=style))
            self.points.clear()

    def stroke(self):
        if len(self.points) >= 2:
            style = self.get_style("stroke", "stroke-width")
            dwg = self.stack[-1]
            last = self.points[0]
            for point in self.points[1:]:
                dwg.add(self.stack[0].line(start=last, end=point, style=style))
                last = point
            self.points.clear()

    def move_to(self, x, y):
        self.points = [(x, y)]

    def line_to(self, x, y):
        self.points.append([x, y])

    def save(self):
        dwg = self.stack[0]
        self.stack.append(dwg.add(dwg.g()))

    def restore(self):
        parent = self.stack[-2]
        dwg = self.stack[-1]
        parent.add(dwg)
        self.stack.pop()

    def translate(self, x, y):
        self.stack[-1].translate(x, y)

    def scale(self, xscale, yscale):
        pass

    def set_transform(self, x, y, z, a, b, c):
        pass

    def rotate(self, angle):
        # comes in radians, need to convert to degrees
        self.stack[-1].rotate(angle * 180 / math.pi)

    def begin_path(self):
        pass

    def close_path(self):
        pass

    def ellipse(self, x, y, radiusX, radiusY, a, b, angle):
        dwg = self.stack[-1]
        style = self.get_style("fill", "stroke", "stroke-width")
        dwg.add(self.stack[0].ellipse(center=(x, y), r=(radiusX, radiusY), style=style))

    def put_image_data(self, scaled, x, y):
        pass

    def create_image_data(sefl, width, height):
        pass
