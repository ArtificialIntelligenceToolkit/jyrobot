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

from .datasets import get_dataset
from .devices.cameras import Camera
from .devices.rangesensors import RangeSensor
from .hit import Hit
from .utils import Color, Line, Point


class Robot:
    def __init__(self, config):
        self.initialize()
        self.from_json(config)

    def __repr__(self):
        return "<Robot(name=%r, position=(%s,%s,%s) v=(%s, %s, %s)>" % (
            self.name,
            self.x,
            self.y,
            self.direction,
            self.va,
            self.vx,
            self.va,
        )

    def initialize(self):
        self.name = "Robbie"
        self.color = Color("red")
        self.doTrace = True
        self.trace = []
        self.max_trace_length = 1000
        self.x = 0  # cm
        self.y = 0  # cm
        self.height = 0.25
        self.direction = 0  # radians
        self.state = ""
        self.debug = False
        self.vx = 0.0  # velocity in x direction, CM per second
        self.vy = 0.0  # velocity in y direction, degrees per second
        self.va = 0.0  # turn velocity
        self.stalled = False
        self.state = ""
        self.bounding_lines = [
            Line(Point(0, 0), Point(0, 0)),
            Line(Point(0, 0), Point(0, 0)),
            Line(Point(0, 0), Point(0, 0)),
            Line(Point(0, 0), Point(0, 0)),
        ]
        self.range_sensors = []
        self.cameras = []
        self.state = ""
        self.image_data = []
        self.get_dataset_image = None
        self.initBoundingBox()

    def from_json(self, config):
        if "name" in config:
            self.name = config["name"]

        if "va" in config:
            self.va = config["va"]
        if "vx" in config:
            self.vx = config["vx"]
        if "vy" in config:
            self.vy = config["vy"]

        if "x" in config:
            self.x = config["x"]
        if "y" in config:
            self.y = config["y"]
        if "direction" in config:
            self.direction = config["direction"] * math.pi / 180

        if "image_data" in config:
            self.image_data = config["image_data"]  # ["dataset", index]
        if len(self.image_data) == 0:
            self.get_dataset_image = None
        else:
            self.get_dataset_image = get_dataset(self.image_data[0])

        if "height" in config:
            self.height = config["height"]  # ratio, 0 to 1 of height

        if "color" in config:
            self.color = Color(config["color"])

        if "body" in config:
            self.body = config["body"]

        if "cameras" in config:
            for cameraConfig in config["cameras"]:
                camera = None
                if cameraConfig["type"] == "Camera":
                    camera = Camera(self, cameraConfig)
                else:
                    print("Unknown camera type:", cameraConfig["type"])

                if camera:
                    self.cameras.append(camera)

        if "rangeSensors" in config:
            for deviceConfig in config["rangeSensors"]:
                device = RangeSensor(self, deviceConfig)
                self.range_sensors.append(device)

    def to_json(self, robot_list):
        robot_json = {
            "name": self.name,
            "va": self.va,
            "vx": self.vx,
            "vy": self.vy,
            "x": self.x,
            "y": self.y,
            "direction": self.direction * 180 / math.pi,
            "image_data": self.image_data,
            "height": self.height,
            "color": str(self.color),
            "body": self.body,
            "cameras": [camera.to_json() for camera in self.cameras],
            "rangeSensors": [device.to_json() for device in self.range_sensors],
        }
        return robot_json

    def forward(self, vx):
        self.vx = vx

    def backward(self, vx):
        self.vx = -vx

    def turn(self, va):
        self.va = va

    def stop(self):
        self.vx = 0.0
        self.vy = 0.0
        self.va = 0.0

    def ccw(self, ax, ay, bx, by, cx, cy):
        # counter clockwise
        return ((cy - ay) * (bx - ax)) > ((by - ay) * (cx - ax))

    def intersect(self, ax, ay, bx, by, cx, cy, dx, dy):
        # Return true if line segments AB and CD intersect
        return self.ccw(ax, ay, cx, cy, dx, dy) != self.ccw(
            bx, by, cx, cy, dx, dy
        ) and (self.ccw(ax, ay, bx, by, cx, cy) != self.ccw(ax, ay, bx, by, dx, dy))

    def coefs(self, p1x, p1y, p2x, p2y):
        A = p1y - p2y
        B = p2x - p1x
        C = p1x * p2y - p2x * p1y
        return [A, B, -C]

    def intersect_coefs(self, L1_0, L1_1, L1_2, L2_0, L2_1, L2_2):
        D = L1_0 * L2_1 - L1_1 * L2_0
        if D != 0:
            Dx = L1_2 * L2_1 - L1_1 * L2_2
            Dy = L1_0 * L2_2 - L1_2 * L2_0
            x1 = Dx / D
            y1 = Dy / D
            return [x1, y1]
        else:
            return None

    def intersect_hit(self, p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y):
        # http:##stackoverflow.com/questions/20677795/find-the-point-of-intersecting-lines
        L1 = self.coefs(p1x, p1y, p2x, p2y)
        L2 = self.coefs(p3x, p3y, p4x, p4y)
        xy = self.intersect_coefs(L1[0], L1[1], L1[2], L2[0], L2[1], L2[2])
        # now check to see on both segments:
        if xy:
            lowx = min(p1x, p2x) - 0.1
            highx = max(p1x, p2x) + 0.1
            lowy = min(p1y, p2y) - 0.1
            highy = max(p1y, p2y) + 0.1
            if (lowx <= xy[0] and xy[0] <= highx) and (
                lowy <= xy[1] and xy[1] <= highy
            ):
                lowx = min(p3x, p4x) - 0.1
                highx = max(p3x, p4x) + 0.1
                lowy = min(p3y, p4y) - 0.1
                highy = max(p3y, p4y) + 0.1
                if (
                    lowx <= xy[0]
                    and xy[0] <= highx
                    and lowy <= xy[1]
                    and xy[1] <= highy
                ):
                    return xy

        return None

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

    def has_image(self):
        return self.get_dataset_image is not None

    def get_image(self, degrees):
        return self.get_dataset_image(self.image_data[1], degrees)

    def castRay(self, x1, y1, a, maxRange):
        # walls and robots
        hits = []
        x2 = math.sin(a) * maxRange + x1
        y2 = math.cos(a) * maxRange + y1

        for wall in self.world.walls:
            # never detect hit with yourself
            if wall.robot is self:
                continue
            for line in wall.lines:
                p1 = line.p1
                p2 = line.p2
                pos = self.intersect_hit(x1, y1, x2, y2, p1.x, p1.y, p2.x, p2.y)
                if pos is not None:
                    dist = self.distance(pos[0], pos[1], x1, y1)
                    height = 1.0 if wall.robot is None else wall.robot.height
                    hits.append(
                        Hit(
                            wall.robot, height, pos[0], pos[1], dist, wall.color, x1, y1
                        )
                    )

        hits.sort(
            key=lambda a: a.distance, reverse=True
        )  # further away first, back to front
        return hits

    def initBoundingBox(self):
        px = self.x
        py = self.y
        pdirection = self.direction
        p1 = self.rotateAround(px, py, 10, pdirection + math.pi / 4 + 0 * math.pi / 2)
        p2 = self.rotateAround(px, py, 10, pdirection + math.pi / 4 + 1 * math.pi / 2)
        p3 = self.rotateAround(px, py, 10, pdirection + math.pi / 4 + 2 * math.pi / 2)
        p4 = self.rotateAround(px, py, 10, pdirection + math.pi / 4 + 3 * math.pi / 2)
        self.updateBoundingBox(p1, p2, p3, p4)

    def updateBoundingBox(self, p1, p2, p3, p4):
        self.bounding_lines[0].p1.x = p1[0]
        self.bounding_lines[0].p1.y = p1[1]
        self.bounding_lines[0].p2.x = p2[0]
        self.bounding_lines[0].p2.y = p2[1]

        self.bounding_lines[1].p1.x = p2[0]
        self.bounding_lines[1].p1.y = p2[1]
        self.bounding_lines[1].p2.x = p3[0]
        self.bounding_lines[1].p2.y = p3[1]

        self.bounding_lines[2].p1.x = p3[0]
        self.bounding_lines[2].p1.y = p3[1]
        self.bounding_lines[2].p2.x = p4[0]
        self.bounding_lines[2].p2.y = p4[1]

        self.bounding_lines[3].p1.x = p4[0]
        self.bounding_lines[3].p1.y = p4[1]
        self.bounding_lines[3].p2.x = p1[0]
        self.bounding_lines[3].p2.y = p1[1]

    def step(self, time_step):
        # self.direction += PI/180
        offset = math.pi / 2
        # proposed positions:
        pdirection = self.direction - self.va * time_step
        tvx = (
            self.vx * math.sin(-pdirection + offset)
            + self.vy * math.cos(-pdirection + offset) * time_step
        )
        tvy = (
            self.vx * math.cos(-pdirection + offset)
            - self.vy * math.sin(-pdirection + offset) * time_step
        )
        px = self.x + tvx
        py = self.y + tvy
        # check to see if collision
        # bounding box:
        # FIXME: use actual bounding box points:
        p1 = self.rotateAround(px, py, 10, pdirection + offset / 2 + 0 * offset)
        p2 = self.rotateAround(px, py, 10, pdirection + offset / 2 + 1 * offset)
        p3 = self.rotateAround(px, py, 10, pdirection + offset / 2 + 2 * offset)
        p4 = self.rotateAround(px, py, 10, pdirection + offset / 2 + 3 * offset)

        self.updateBoundingBox(p1, p2, p3, p4)

        self.stalled = False
        # if intersection, can't move:
        for wall in self.world.walls:
            if wall.robot is self:  # if yourself, don't check for collision
                continue
            for line in wall.lines:
                w1 = line.p1
                w2 = line.p2
                if (
                    self.intersect(p1[0], p1[1], p2[0], p2[1], w1.x, w1.y, w2.x, w2.y)
                    or self.intersect(
                        p2[0], p2[1], p3[0], p3[1], w1.x, w1.y, w2.x, w2.y
                    )
                    or self.intersect(
                        p3[0], p3[1], p4[0], p4[1], w1.x, w1.y, w2.x, w2.y
                    )
                    or self.intersect(
                        p4[0], p4[1], p1[0], p1[1], w1.x, w1.y, w2.x, w2.y
                    )
                ):
                    self.stalled = True
                    break

        if not self.stalled:
            # if no intersection, make move
            self.x = px
            self.y = py
            self.direction = pdirection

        self.trace.append((Point(self.x, self.y), self.direction))

        # Range Sensors:
        for range_sensor in self.range_sensors:
            range_sensor.step(time_step)

        # Cameras:
        for camera in self.cameras:
            camera.step(time_step)

    def update(self):
        self.initBoundingBox()
        # Range Sensors:
        for range_sensor in self.range_sensors:
            range_sensor.update()

        # Cameras:
        for camera in self.cameras:
            camera.update()

    def rotateAround(self, x1, y1, length, angle):
        return [x1 + length * math.cos(-angle), y1 - length * math.sin(-angle)]

    def draw(self, canvas):
        if self.doTrace:
            canvas.strokeStyle(Color(200, 200, 200), 1)
            canvas.beginShape()
            # The last max_trace_length points:
            for (point, direction) in self.trace[-self.max_trace_length :]:
                canvas.vertex(point.x, point.y)

            canvas.stroke()

        if self.debug:
            canvas.strokeStyle(Color(255), 1)
            canvas.line(
                self.bounding_lines[0].p1.x,
                self.bounding_lines[0].p1.y,
                self.bounding_lines[0].p2.x,
                self.bounding_lines[0].p2.y,
            )

            canvas.line(
                self.bounding_lines[1].p1.x,
                self.bounding_lines[1].p1.y,
                self.bounding_lines[1].p2.x,
                self.bounding_lines[1].p2.y,
            )

            canvas.line(
                self.bounding_lines[2].p1.x,
                self.bounding_lines[2].p1.y,
                self.bounding_lines[2].p2.x,
                self.bounding_lines[2].p2.y,
            )

            canvas.line(
                self.bounding_lines[3].p1.x,
                self.bounding_lines[3].p1.y,
                self.bounding_lines[3].p2.x,
                self.bounding_lines[3].p2.y,
            )

        canvas.pushMatrix()
        canvas.translate(self.x, self.y)
        canvas.rotate(self.direction)

        # body:
        if self.stalled:
            canvas.fill(Color(128, 128, 128))
            canvas.strokeStyle(Color(255), 1)
        else:
            canvas.fill(self.color)
            canvas.noStroke()

        canvas.beginShape()
        for i in range(len(self.body)):
            canvas.vertex(self.body[i][0], self.body[i][1])

        canvas.endShape()
        canvas.noStroke()
        # Draw wheels:
        canvas.fill(Color(0))
        canvas.rect(-3.33, -7.67, 6.33, 1.67)
        canvas.rect(-3.33, 6.0, 6.33, 1.67)
        # hole:
        canvas.fill(Color(0, 64, 0))
        canvas.strokeStyle(None, 0)
        canvas.ellipse(0, 0, 1.67, 1.67)

        for camera in self.cameras:
            camera.draw(canvas)

        canvas.popMatrix()

        for range_sensor in self.range_sensors:
            range_sensor.draw(canvas)
