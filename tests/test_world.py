# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from jyrobot import World


def test_world():
    world = World()

    assert world.width == 500
    assert world.height == 250
