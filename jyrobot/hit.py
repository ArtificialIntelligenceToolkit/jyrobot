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
    def __init__(self, height, x, y, distance, color, start_x, start_y):
        self.height = height
        self.x = x
        self.y = y
        self.distance = distance
        self.color = color
        self.start_x = start_x
