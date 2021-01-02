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

from ..colors import YELLOW
from ..utils import distance


class LightSensor:
    def __init__(self, **config):
        self.robot = None
        self.initialize()
        self.from_json(config)

    def initialize(self):
        self.type = "light"
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
        pass

    def draw(self, backend):
        backend.set_fill_style(YELLOW)
        backend.draw_circle(self.position[0], self.position[1], 2)

    def get_reading(self):
        pass
        # for light in robot.physics.lights: # for each light source:
        #     x, y, brightness, light_rgb = light.x, light.y, light.brightness, light.rgb
        #     # FIXME: never using light_rgb
        #     seg = Segment((x,y), (gx, gy))
        #     seg_length = seg.length()
        #     a = -seg.angle() + PIOVER2
        #     dist, hit, obj = robot.physics.castRay(robot, x, y, a, seg_length - .1,
        #                                            ignoreRobot=self.ignore, rayType="light")
        #     # scaled over distance, but not zero:
        #     dist_to_light = min(max(seg_length, min_dist_meters), self.maxRange) / self.maxRange
        #     min_scaled_d = min_dist_meters/self.maxRange
        #     if self.lightMode == "ambient":
        #         maxValueAmbient = 1.0 / min_scaled_d
        #         intensity = (1.0 / dist_to_light) / maxValueAmbient
        #     elif self.lightMode == "direct":
        #         maxValueIntensity = 1.0 / (min_scaled_d ** 2)
        #         intensity = (1.0 / (dist_to_light ** 2)) / maxValueIntensity
        #     elif self.lightMode == "linear":
        #         intensity = 1.0 - dist_to_light
        #     if hit:
        #         intensity /= 2.0 # cut in half if in shadow
        #     sum += intensity * brightness
        #     if not hit: # no hit means it has a clear shot:
        #         if robot.display["devices"] == 1:
        #             robot.drawRay("light", x, y, gx, gy, "orange")
        #     else:
        #         if robot.display["devices"] == 1:
        #             robot.drawRay("lightBlocked", x, y, hit[0], hit[1], "purple")
        # self.scan[i] = sum
