# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from collections import OrderedDict
from datetime import datetime, timedelta
from functools import wraps

from .color_data import COLORS


def json_dump(config, fp, sort_keys=True, indent=4):
    dumps(fp, config, sort_keys=sort_keys, indent=indent)


def dumps(fp, obj, level=0, sort_keys=True, indent=4, newline="\n", space=" "):
    if isinstance(obj, dict):
        if sort_keys:
            obj = OrderedDict({key: obj[key] for key in sorted(obj.keys())})
        fp.write(newline + (space * indent * level) + "{" + newline)
        comma = ""
        for key, value in obj.items():
            fp.write(comma)
            comma = "," + newline
            fp.write(space * indent * (level + 1))
            fp.write('"%s":%s' % (key, space))
            dumps(fp, value, level + 1, sort_keys, indent, newline, space)
        fp.write(newline + (space * indent * level) + "}")
    elif isinstance(obj, str):
        fp.write('"%s"' % obj)
    elif isinstance(obj, (list, tuple)):
        if len(obj) == 0:
            fp.write("[]")
        else:
            fp.write(newline + (space * indent * level) + "[")
            # fp.write("[")
            comma = ""
            for item in obj:
                fp.write(comma)
                comma = ", "
                dumps(fp, item, level + 1, sort_keys, indent, newline, space)
            # each on their own line
            if len(obj) > 2:
                fp.write(newline + (space * indent * level))
            fp.write("]")
    elif isinstance(obj, bool):
        fp.write("true" if obj else "false")
    elif isinstance(obj, int):
        fp.write(str(obj))
    elif obj is None:
        fp.write("null")
    elif isinstance(obj, float):
        fp.write("%.7g" % obj)
    else:
        raise TypeError("Unknown object %r for json serialization" % obj)


class throttle(object):
    """
    Decorator that prevents a function from being called more than once every
    time period.
    To create a function that cannot be called more than once a minute:
        @throttle(minutes=1)
        def my_fun():
            pass
    """

    def __init__(self, seconds=0, minutes=0, hours=0):
        self.throttle_period = timedelta(seconds=seconds, minutes=minutes, hours=hours)
        self.time_of_last_call = datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            time_since_last_call = now - self.time_of_last_call

            if time_since_last_call > self.throttle_period:
                self.time_of_last_call = now
                return fn(*args, **kwargs)

        return wrapper


class Color:
    def __init__(self, red, green=None, blue=None, alpha=None):
        self.name = None
        if isinstance(red, str):
            if red.startswith("#"):
                # encoded hex color
                red, green, blue, alpha = self.hex_to_rgba(red)
            else:
                # color name
                self.name = red
                hex_string = COLORS.get(red, "#00000000")
                red, green, blue, alpha = self.hex_to_rgba(hex_string)
        elif isinstance(red, (list, tuple)):
            if len(red) == 3:
                red, green, blue = red
                alpha = 255
            else:
                red, green, blue, alpha = red

        self.red = red
        if green is not None:
            self.green = green
        else:
            self.green = red
        if blue is not None:
            self.blue = blue
        else:
            self.blue = red
        if alpha is not None:
            self.alpha = alpha
        else:
            self.alpha = 255

    def hex_to_rgba(self, hex_string):
        r_hex = hex_string[1:3]
        g_hex = hex_string[3:5]
        b_hex = hex_string[5:7]
        if len(hex_string) > 7:
            a_hex = hex_string[7:9]
        else:
            a_hex = "FF"
        return int(r_hex, 16), int(g_hex, 16), int(b_hex, 16), int(a_hex, 16)

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return self.to_hexcode()

    def __repr__(self):
        return "<Color%s>" % (self.to_tuple(),)

    def to_tuple(self):
        return (int(self.red), int(self.green), int(self.blue), int(self.alpha))

    def rgb(self):
        if int(self.alpha) == 255:
            return "rgb(%d,%d,%d)" % (int(self.red), int(self.green), int(self.blue))
        else:
            return "rgb(%d,%d,%d,%d)" % (
                int(self.red),
                int(self.green),
                int(self.blue),
                int(self.alpha),
            )

    def to_hexcode(self):
        return "#%02X%02X%02X%02X" % self.to_tuple()


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point(%s,%s)" % (self.x, self.y)


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        return "Line(%s,%s)" % (self.p1, self.p2)
