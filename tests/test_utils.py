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

from jyrobot.utils import arange, distance


def test_distance():
    x1, y1 = 0, 0

    for (x2, y2) in [[1, 1], [-1, -1], [-1, 1], [1, -1]]:
        assert distance(x1, y1, x2, y2) == math.sqrt(2)


def test_arange():
    assert [1, 2, 3, 4, 5] == [x for x in arange(1, 5, 1)]


def test_arange_neg():
    assert [5, 4, 3, 2, 1] == [x for x in arange(5, 1, -1)]
