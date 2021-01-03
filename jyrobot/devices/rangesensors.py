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

from ..utils import Color, arange, distance


class RangeSensor:
    """
    A range sensor that reads "reading" when
    no obstacle has been detected. "reading" is
    a ratio of distance/max, and "distance" is
    the reading in CM.
    """

    def __init__(self, **config):
        self.robot = None
        self.initialize()
        self.from_json(config)

    def initialize(self):
        self.type = "ir"
        self.time = 0.0
        self.reading = 1.0
        self.position = [8, 0]
        self.dist_from_center = distance(0, 0, self.position[0], self.position[1])
        self.dir_from_center = math.atan2(-self.position[0], self.position[1])
        self.direction = 0  # comes in degrees, save as radians
        self.max = 20  # CM
        self.width = 1.0  # radians
        self.distance = self.reading * self.max

    def watch(self, title="Range Sensor:"):
        from ..watchers import AttributesWatcher

        if self.robot is None or self.robot.world is None:
            print("ERROR: can't watch until added to robot, and robot is in world")
            return None

        watcher = AttributesWatcher(
            self, "reading", "distance", title=title, labels=["Reading:", "Distance:"]
        )
        self.robot.world.watchers.append(watcher)
        return watcher.widget

    def from_json(self, config):
        if "position" in config:
            self.position = config["position"]
            # Get location of sensor, doesn't change once position is set:
            self.dist_from_center = distance(0, 0, self.position[0], self.position[1])
            self.dir_from_center = math.atan2(-self.position[0], self.position[1])
        if "direction" in config:
            self.direction = config["direction"] * math.pi / 180  # save as radians
        if "max" in config:
            self.max = config["max"]
        if "width" in config:
            self.width = config["width"] * math.pi / 180  # save as radians
            if self.width == 0:
                self.type = "laser"
        self.distance = self.reading * self.max

    def to_json(self):
        config = {
            "class": self.__class__.__name__,
            "position": self.position,
            "direction": self.direction * 180 / math.pi,  # save as degrees
            "max": self.max,
            "width": self.width * 180 / math.pi,  # save as degrees
        }
        return config

    def __repr__(self):
        return "<RangeSensor angle=%r, range=%r, width=%r>" % (
            round(self.direction * 180 / math.pi, 1),
            self.max,
            round(self.width * 180 / math.pi, 1),
        )

    def step(self, time_step):
        pass

    def update(self, debug_list=None):
        # Update timestamp:
        self.time = self.robot.world.time
        # This changes:
        p = self.robot.rotate_around(
            self.robot.x,
            self.robot.y,
            self.dist_from_center,
            self.robot.direction + self.dir_from_center + math.pi / 2,
        )

        if debug_list is not None:
            debug_list.append(("draw_ellipse", (p[0], p[1], 2, 2)))

        self.set_reading(1.0)
        if self.width != 0:
            for incr in arange(-self.width / 2, self.width / 2, self.width / 2):
                hits = self.robot.cast_ray(
                    p[0],
                    p[1],
                    -self.robot.direction + math.pi / 2.0 + incr - self.direction,
                    self.max,
                )
                if hits:
                    if debug_list is not None:
                        debug_list.append(
                            ("draw_ellipse", (hits[-1].x, hits[-1].y, 2, 2))
                        )
                    # Closest hit:
                    if hits[-1].distance < self.get_distance():
                        self.set_distance(hits[-1].distance)
        else:
            hits = self.robot.cast_ray(
                p[0],
                p[1],
                -self.robot.direction + math.pi / 2.0 - self.direction,
                self.max,
            )
            if hits:
                if debug_list is not None:
                    debug_list.append(("draw_ellipse", (hits[-1].x, hits[-1].y, 2, 2)))
                # Closest hit:
                if hits[-1].distance < self.get_distance():
                    self.set_distance(hits[-1].distance)

    def draw(self, backend):
        backend.set_fill(Color(128, 0, 128, 64))
        dist = self.get_distance()
        if self.width > 0:
            if self.get_reading() < 1.0:
                backend.strokeStyle(Color(255), 1)
            else:
                backend.strokeStyle(Color(0), 1)

            backend.draw_arc(
                self.position[0],
                self.position[1],
                dist,
                dist,
                self.direction - self.width / 2,
                self.direction + self.width / 2,
            )
        else:
            if self.get_reading() < 1.0:
                backend.strokeStyle(Color(255), 1)
            else:
                backend.strokeStyle(Color(128, 0, 128, 64), 1)

            backend.draw_line(
                self.position[0], self.position[1], dist + self.position[0], 0
            )

    def get_distance(self):
        return self.distance

    def get_reading(self):
        return self.reading

    def set_distance(self, distance):
        self.distance = distance
        self.reading = distance / self.max

    def set_reading(self, reading):
        self.reading = reading
        self.distance = reading * self.max
