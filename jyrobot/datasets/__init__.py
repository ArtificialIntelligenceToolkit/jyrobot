# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import os

_jyrobot_base_dir = os.path.expanduser("~")
if not os.access(_jyrobot_base_dir, os.W_OK):
    _jyrobot_base_dir = "/tmp"

_jyrobot_dir = os.path.join(_jyrobot_base_dir, ".jyrobot")

if not os.path.exists(_jyrobot_dir):
    try:
        os.makedirs(_jyrobot_dir)
    except OSError:
        pass
