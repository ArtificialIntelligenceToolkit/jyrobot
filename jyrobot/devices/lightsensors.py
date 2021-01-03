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

from ..colors import PURPLE, YELLOW
from ..utils import distance


class LightSensor:
    def __init__(self, **config):
        self.robot = None
        self.initialize()
        self.from_json(config)

    def initialize(self):
        self.type = "light"
        self.value = 0.0
        # FIXME: add to config
        self.multiplier = 1000  # CM
        self.position = [0, 0]
        self.dist_from_center = distance(0, 0, self.position[0], self.position[1])
        self.dir_from_center = math.atan2(-self.position[0], self.position[1])

    def from_json(self, config):
        if "position" in config:
            self.position = config["position"]
            # Get location of sensor, doesn't change once position is set:
            self.dist_from_center = distance(0, 0, self.position[0], self.position[1])
            self.dir_from_center = math.atan2(-self.position[0], self.position[1])

    def to_json(self):
        config = {
            "class": self.__class__.__name__,
            "position": self.position,
        }
        return config

    def step(self, time_step):
        pass

    def update(self, debug_list=None):
        self.value = 0
        # Location of sensor:
        p = self.robot.rotate_around(
            self.robot.x,
            self.robot.y,
            self.dist_from_center,
            self.robot.direction + self.dir_from_center + math.pi / 2,
        )
        for bulb in self.robot.world.bulbs:  # for each light source:
            x, y, z, brightness, light_color = (  # noqa: F841
                bulb.x,
                bulb.y,
                bulb.z,
                bulb.brightness,
                bulb.color,
            )
            # FIXME: use bulb_color for something?

            angle = math.atan2(x - p[0], y - p[1])
            dist = distance(x, y, p[0], p[1])
            hits = self.robot.cast_ray(p[0], p[1], angle, dist)
            if debug_list is not None:
                debug_list.append(("draw_circle", (p[0], p[1], 2)))
                debug_list.append(("draw_circle", (x, y, 2)))

                for hit in hits:
                    debug_list.append(("set_fill_style", (PURPLE,)))
                    debug_list.append(("draw_circle", (hit.x, hit.y, 2)))

            if len(hits) == 0:  # nothing blocking! we can see the light
                # Make sure not zero:
                self.value += brightness * self.multiplier / (dist ** 2)
                if debug_list is not None:
                    debug_list.append(("strokeStyle", (PURPLE, 1)))
                    debug_list.append(("draw_line", (x, y, p[0], p[1])))

    def draw(self, backend):
        backend.set_fill_style(YELLOW)
        backend.draw_circle(self.position[0], self.position[1], 2)

    def get_reading(self):
        return self.value

    def watch(self):
        from ..widgets import TextWatcher

        watcher = TextWatcher(self, "value", "Light:")
        self.robot.watchers.append(watcher)
        return watcher.widget
