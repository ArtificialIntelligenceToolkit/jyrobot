# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from jyrobot import Robot

def test_robot():
    robot = Robot()

    assert (robot.x, robot.y, robot.direction) == (0, 0, 0)


