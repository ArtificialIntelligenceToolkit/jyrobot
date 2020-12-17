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

from ..utils import Color


def arange(start, stop, step):
    current = start
    while current <= stop:
        yield current
        current += step


class RangeSensor:
    """
       A range sensor that reads "reading" when
       no obstacle has been detected. "reading" is
       a ratio of distance/max, and "distance" is
       the reading in CM.
    """

    def __init__(self, robot, config):
        self.robot = robot
        self.reading = 1.0
        self.position = 10
        self.direction = 0  # comes in degrees, save as radians
        self.max = 100
        self.width = 1.0
        self.distance = self.reading * self.max
        self.from_json(config)

    def from_json(self, config):
        if "position" in config:
            self.position = config["position"]
        if "direction" in config:
            self.direction = config["direction"] * math.pi / 180  # save as radians
        if "max" in config:
            self.max = config["max"]
        if "width" in config:
            self.width = config["width"]

        self.distance = self.reading * self.max

    def to_json(self):
        config = {
            "position": self.position,
            "direction": self.direction * 180 / math.pi,  # save as degrees
            "max": self.max,
            "width": self.width,
        }
        return config

    def step(self, time_step):
        pass

    def update(self):
        p = self.robot.rotateAround(
            self.robot.x,
            self.robot.y,
            self.position,
            self.robot.direction + self.direction,
        )
        self.setReading(1.0)
        if self.width != 0:
            for incr in arange(-self.width / 2, self.width / 2, self.width / 2):
                hits = self.robot.castRay(
                    p[0], p[1], -self.robot.direction + math.pi / 2.0 + incr, self.max,
                )
                if hits:
                    # Closest hit:
                    if hits[-1].distance < self.getDistance():
                        self.setDistance(hits[-1].distance)
        else:
            hits = self.robot.castRay(
                p[0], p[1], -self.robot.direction + math.pi / 2.0, self.max
            )
            if hits:
                # Closest hit:
                if hits[-1].distance < self.getDistance():
                    self.setDistance(hits[-1].distance)

    def draw(self, canvas):
        if self.getReading() < 1.0:
            canvas.strokeStyle(Color(255), 1)
        else:
            canvas.strokeStyle(Color(0), 1)

        canvas.fill(Color(128, 0, 128, 64))
        p1 = self.robot.rotateAround(
            self.robot.x,
            self.robot.y,
            self.position,
            self.robot.direction + self.direction,
        )
        dist = self.getDistance()
        if self.width > 0:
            canvas.arc(
                p1[0],
                p1[1],
                dist,
                dist,
                self.robot.direction - self.width / 2,
                self.robot.direction + self.width / 2,
            )
        else:
            end = self.robot.rotateAround(
                p1[0], p1[1], dist, self.direction + self.direction
            )
            canvas.line(p1[0], p1[1], end[0], end[1])

    def getDistance(self):
        return self.distance

    def getReading(self):
        return self.reading

    def setDistance(self, distance):
        self.distance = distance
        self.reading = distance / self.max

    def setReading(self, reading):
        self.reading = reading
        self.distance = reading * self.max
