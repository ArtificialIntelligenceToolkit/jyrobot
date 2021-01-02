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

from jyrobot.utils import distance


def test_distance():
    x1, y1 = 0, 0

    for (x2, y2) in [[1, 1], [-1, -1], [-1, 1], [1, -1]]:
        assert distance(x1, y1, x2, y2) == math.sqrt(2)
