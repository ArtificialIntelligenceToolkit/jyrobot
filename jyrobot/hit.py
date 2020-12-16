# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************


class Hit:
    def __init__(self, robot, height, x, y, distance, color, start_x, start_y):
        self.robot = robot
        self.height = height
        self.x = x
        self.y = y
        self.distance = distance
        self.color = color
        self.start_x = start_x
        self.start_y = start_y

    def __repr__(self):
        return "<Hit(%s,%s) distance=%s, height=%s>" % (
            self.x,
            self.y,
            self.distance,
            self.height,
        )
