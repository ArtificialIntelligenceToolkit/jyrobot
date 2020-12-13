# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from ._version import __version__

config = {
    "world": {
        "width": 500,
        "height": 250,
        "boxes": [
            {"color": [0, 0, 0], "p1": {"x": 100, "y": 0}, "p2": {"x": 110, "y": 110}},
            {
                "color": [255, 0, 255],
                "p1": {"x": 200, "y": 95},
                "p2": {"x": 210, "y": 170},
            },
            {
                "color": [255, 255, 0],
                "p1": {"x": 300, "y": 0},
                "p2": {"x": 310, "y": 95},
            },
            {
                "color": [255, 128, 0],
                "p1": {"x": 300, "y": 190},
                "p2": {"x": 310, "y": 250},
            },
        ],
    },
    "robots": [
        {
            "name": "Red",
            "x": 430,
            "y": 50,
            "direction": 180,
            "color": [255, 0, 0],
            "cameras": [
                {
                    "type": "Camera",
                    "width": 256,
                    "height": 128,
                    "colorsFadeWithDistance": 1.0,
                    "angle": 60,
                }
            ],
            "rangeSensors": [
                {"position": 8.2, "direction": 0, "max": 100, "width": 0.05},
                {"position": 8.2, "direction": 22.5, "max": 20, "width": 1.0},
                {"position": 8.2, "direction": -22.5, "max": 20, "width": 1.0},
            ],
            "body": [
                [4.17, 5.0],
                [4.17, 6.67],
                [5.83, 5.83],
                [5.83, 5.0],
                [7.5, 5.0],
                [7.5, -5.0],
                [5.83, -5.0],
                [5.83, -5.83],
                [4.17, -6.67],
                [4.17, -5.0],
                [-4.17, -5.0],
                [-4.17, -6.67],
                [-5.83, -5.83],
                [-6.67, -5.0],
                [-7.5, -4.17],
                [-7.5, 4.17],
                [-6.67, 5.0],
                [-5.83, 5.83],
                [-4.17, 6.67],
                [-4.17, 5.0],
            ],
        },
        {
            "name": "Blue",
            "x": 30,
            "y": 50,
            "direction": 0,
            "color": [0, 0, 255],
            "cameras": [
                {
                    "type": "DepthCamera",
                    "width": 256,
                    "height": 128,
                    "colorsFadeWithDistance": 1.0,
                    "angle": 60,
                },
                {
                    "type": "Camera",
                    "width": 256,
                    "height": 128,
                    "colorsFadeWithDistance": 1.0,
                    "angle": 60,
                },
                {
                    "type": "Camera",
                    "width": 256,
                    "height": 128,
                    "colorsFadeWithDistance": 1.0,
                    "angle": 30,
                },
            ],
            "rangeSensors": [
                {"position": 8.2, "direction": 0, "max": 100, "width": 0.05},
                {"position": 8.2, "direction": 22.5, "max": 20, "width": 1.0},
                {"position": 8.2, "direction": -22.5, "max": 20, "width": 1.0},
            ],
            "body": [
                [4.17, 5.0],
                [4.17, 6.67],
                [5.83, 5.83],
                [5.83, 5.0],
                [7.5, 5.0],
                [7.5, -5.0],
                [5.83, -5.0],
                [5.83, -5.83],
                [4.17, -6.67],
                [4.17, -5.0],
                [-4.17, -5.0],
                [-4.17, -6.67],
                [-5.83, -5.83],
                [-6.67, -5.0],
                [-7.5, -4.17],
                [-7.5, 4.17],
                [-6.67, 5.0],
                [-5.83, 5.83],
                [-4.17, 6.67],
                [-4.17, 5.0],
            ],
        },
    ],
}
