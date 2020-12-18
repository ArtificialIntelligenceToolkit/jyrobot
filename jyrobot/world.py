# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import io
import json
import math
import os
import signal
import sys
import time
from contextlib import contextmanager

from ipycanvas import hold_canvas
from ipylab import JupyterFrontEnd, Panel
from IPython.display import clear_output, display
from ipywidgets import Box
from PIL import Image

from .canvas import Canvas
from .robot import Robot
from .utils import Color, Line, Point, throttle

DEFAULT_HANDLER = signal.getsignal(signal.SIGINT)


class Wall:
    def __init__(self, color, robot, *lines):
        self.color = color
        self.robot = robot
        self.lines = lines

    def __repr__(self):
        return "Wall(%r, %r, %r)" % (self.color, self.robot, self.lines)


class Robots:
    def __init__(self, world):
        self.world = world

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.world._robots[item]
        elif isinstance(item, str):
            for robot in self.world._robots:
                if item.lower() == robot.name.lower():
                    return robot
        return None

    def __repr__(self):
        with io.StringIO() as fp:
            if len(self.world._robots) == 0:
                print("This world has no robots.", file=fp)
            else:
                print("Robots:", file=fp)
                print("-" * 25, file=fp)
                for i, robot in enumerate(self.world._robots):
                    print("    robot[%s]: %r" % (i, robot.name), file=fp)
            return fp.getvalue()


class World:
    def __init__(self, config=None):
        self.debug = False
        self.robot = Robots(self)
        self.real_time = True
        self.canvas = None
        self.config = config if config is not None else {}
        self.init()  # default values
        self.reset()  # from config
        # Two updates to force all robots to see each other
        self.update()
        self.update()
        self.draw()

    def _repr_png_(self):
        return self.takePicture()._repr_png_()

    def takePicture(self):
        return self.canvas.takePicture()

    def init(self):
        self.width = 500
        self.height = 250
        self.scale = 3.0
        self.stop = False  # should stop?
        self.time_step = 0.10  # seconds
        self.time = 0.0  # seconds
        self.at_x = 0
        self.at_y = 0
        self.boundary_wall = True
        self.boundary_wall_width = 1
        self.boundary_wall_color = Color(128, 0, 128)
        self.ground_color = Color(0, 128, 0)
        self._robots = []
        self.walls = []

    def reset(self):
        self.init()
        self.from_json(self.config)
        self.draw()

    def from_json(self, config):
        self.config = config
        if "width" in config:
            self.width = config["width"]
        if "height" in config:
            self.height = config["height"]
        if "scale" in config:
            self.scale = config["scale"]
        if "boundary_wall" in config:
            self.boundary_wall = config["boundary_wall"]
        if "boundary_wall_color" in config:
            self.boundary_wall_color = Color(config["boundary_wall_color"])
        if "boundary_wall_width" in config:
            self.boundary_wall_width = config["boundary_wall_width"]
        if "ground_color" in config:
            self.ground_color = Color(config["ground_color"])

        if self.boundary_wall:
            p1 = Point(0, 0)
            p2 = Point(0, self.height)
            p3 = Point(self.width, self.height)
            p4 = Point(self.width, 0)
            ## Not a box, but surround area with four boundaries:
            self.walls.extend(
                [
                    Wall(self.boundary_wall_color, None, Line(p1, p2)),
                    Wall(self.boundary_wall_color, None, Line(p2, p3)),
                    Wall(self.boundary_wall_color, None, Line(p3, p4)),
                    Wall(self.boundary_wall_color, None, Line(p4, p1)),
                ]
            )
        for wall in config.get("walls", []):
            # Walls are "boxes"... 4 lines:
            self.addWall(
                Color(wall["color"]),
                wall["p1"]["x"],
                wall["p1"]["y"],
                wall["p2"]["x"],
                wall["p2"]["y"],
            )
        ## Create robot, and add to world:
        for robotConfig in self.config.get("robots", []):
            robot = Robot(robotConfig)
            self.addRobot(robot)
        # Create the canvas is first time:
        if self.canvas is None:
            self.canvas = Canvas(self.width, self.height, self.scale)
        # Update the canvas if different from original canvas
        self.update_size()
        self.update_scale()

    def to_json(self):
        config = {
            "width": int(self.width),
            "height": int(self.height),
            "scale": self.scale,
            "boundary_wall": self.boundary_wall,  # bool
            "boundary_wall_color": str(self.boundary_wall_color),
            "boundary_wall_width": self.boundary_wall_width,
            "ground_color": str(self.ground_color),
            "walls": [],
            "robots": [],
        }
        for wall in self.walls:
            if len(wall.lines) == 4 and wall.robot is None:
                w = {
                    "color": str(wall.color),
                    "p1": {"x": wall.lines[0].p1.x, "y": wall.lines[0].p1.y,},
                    "p2": {"x": wall.lines[2].p1.x, "y": wall.lines[2].p1.y,},
                }
                config["walls"].append(w)

        for robot in self._robots:
            config["robots"].append(robot.to_json(config["robots"]))

        return config

    def save(self):
        if "filename" in self.config and os.path.exists(self.config["filename"]):
            with open(self.config["filename"], "w") as fp:
                json.dump(self.to_json(), fp, sort_keys=True, indent=4)
        else:
            raise Exception("unable to save world config file")

    def save_as(self, filename):
        with open(filename, "w") as fp:
            json.dump(self.to_json(), fp, sort_keys=True, indent=4)

    def update_size(self):
        self.canvas.change_size(self.width, self.height)

    def update_scale(self):
        self.canvas.change_scale(self.scale)

    def set_scale(self, scale):
        self.scale = scale
        self.canvas.change_scale(self.scale)
        # Save with config
        self.config["scale"] = self.scale
        self.draw()

    def gallery(self, *images):
        """
        Construct a gallery of images
        """
        gallery_size = math.ceil(math.sqrt(len(images)))
        size = images[0].size

        gallery_image = Image.new(
            mode="RGBA",
            size=(int(gallery_size * size[0]), int(gallery_size * size[1])),
            color=(0, 0, 0, 0),
        )

        for i, image in enumerate(images):
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            location = (
                int((i % gallery_size) * size[0]),
                int((i // gallery_size) * size[1]),
            )
            gallery_image.paste(image, location)
        return gallery_image

    def display(self, *objects, **kwargs):
        if all([isinstance(obj, Image.Image) for obj in objects]) and len(objects) > 1:
            objects = [self.gallery(*objects)]
        clear_output(wait=kwargs.get("wait", True))
        display(*objects)

    def watch(self, where="inline", clear=True, **layout):
        if where in ["panel", "left", "right"]:
            app = JupyterFrontEnd()
            panel = Panel()

            if clear:
                for widget in list(app.shell.widgets.values()):
                    if hasattr(widget, "title") and widget.title.label.startswith(
                        "Jyrobot"
                    ):
                        widget.close()

            if where == "panel":
                # Close all Jyro widgets
                defaults = {"width": "100%", "height": "auto"}
                defaults.update(layout)
                box = Box()
                for keyword in defaults:
                    setattr(box.layout, keyword, defaults[keyword])
                    box.children = [self.canvas.gc]

                panel.children = [box]
                panel.title.label = "Jyrobot Simulator"
                app.shell.add(panel, "main", {"mode": "split-right"})
            elif where == "left":
                panel.children = [self.canvas.gc]
                panel.title.label = "Jyrobot Simulator"
                app.shell.add(panel, "left", {"rank": 10000})
                app.shell.expand_left()
            elif where == "right":
                panel.children = [self.canvas.gc]
                panel.title.label = "Jyrobot Simulator"
                app.shell.add(panel, "right", {"rank": 0})
                app.shell.expand_right()
        else:  # "inline", or something else
            defaults = {"max_width": "600px"}
            defaults.update(layout)
            box = Box()
            for keyword in defaults:
                setattr(box.layout, keyword, defaults[keyword])
            box.children = [self.canvas.gc]
            display(box)

    def addWall(self, color, x1, y1, x2, y2):
        p1 = Point(x1, y1)
        p2 = Point(x2, y1)
        p3 = Point(x2, y2)
        p4 = Point(x1, y2)
        ## Pairs of points make Line:
        wall = Wall(color, None, Line(p1, p2), Line(p2, p3), Line(p3, p4), Line(p4, p1))
        self.walls.append(wall)

    def addRobot(self, robot):
        self._robots.append(robot)
        robot.world = self
        # Bounding lines form a wall:
        wall = Wall(robot.color, robot, *robot.bounding_lines)
        self.walls.append(wall)

    def signal_handler(self, *args, **kwargs):
        self.stop = True

    @contextmanager
    def no_interrupt(self):
        """
        Suspends signal handling execution
        """
        self.stop = False
        signal.signal(signal.SIGINT, self.signal_handler)

        try:
            yield None
        finally:
            signal.signal(signal.SIGINT, DEFAULT_HANDLER)

    def run(self, function=None, time_step=None, show=True):
        time_step = time_step if time_step is not None else self.time_step
        self.steps(sys.maxsize, function, time_step, show)

    def seconds(self, seconds=5.0, function=None, time_step=None, show=True):
        time_step = time_step if time_step is not None else self.time_step
        count = round(seconds / time_step)
        self.steps(count, function, time_step, show)

    def steps(self, steps=1, function=None, time_step=None, show=True):
        """
        Args:
            function - (optional) either a single function that takes the
                world, or a list of functions (or None) that each take
                a robot. If any function returns True, then simulation will
                stop.
        """
        time_step = time_step if time_step is not None else self.time_step
        with self.no_interrupt():
            for step in range(steps):
                if self.stop:
                    return
                self.step(time_step, show=show)
                if function is not None:
                    if isinstance(function, (list, tuple)):
                        # Deterministically run robots round-robin:
                        stop = any(
                            [
                                function[i](self._robots[i])
                                for i in range(len(function))
                                if function[i] is not None
                            ]
                        )
                    else:
                        stop = function(self)
                    if stop:
                        return

    def step(self, time_step=None, show=True):
        time_step = time_step if time_step is not None else self.time_step
        for robot in self._robots:
            robot.step(time_step)
        self.time += time_step
        self.update(show)

    def update(self, show=True):
        ## Update robots:
        debug = [] if self.debug else None
        for robot in self._robots:
            robot.update(debug)
        if show:
            self.draw()
            if debug is not None:
                for command, args in debug:
                    getattr(self.canvas, command)(*args)
            if self.real_time:
                time.sleep(0.001)

    @throttle(0.1)
    def draw(self, canvas=None):
        canvas = canvas if canvas is not None else self.canvas
        if canvas is None:
            return

        with hold_canvas(canvas.gc):
            canvas.clear()
            canvas.noStroke()
            canvas.fill(self.ground_color)
            canvas.rect(self.at_x, self.at_y, self.width, self.height)
            ## Draw walls:
            for wall in self.walls:
                if len(wall.lines) >= 1 and wall.robot is None:
                    c = wall.color
                    canvas.noStroke()
                    canvas.fill(c)
                    canvas.beginShape()
                    for line in wall.lines:
                        canvas.vertex(line.p1.x, line.p1.y)
                        canvas.vertex(line.p2.x, line.p2.y)

                    canvas.endShape()

            ## Draw borders:
            for wall in self.walls:
                c = wall.color
                if len(wall.lines) == 1:
                    canvas.strokeStyle(c, 3)
                    canvas.line(
                        wall.lines[0].p1.x,
                        wall.lines[0].p1.y,
                        wall.lines[0].p2.x,
                        wall.lines[0].p2.y,
                    )
                    canvas.lineWidth(1)
                    canvas.noStroke()

            ## Draw robots:
            for robot in self._robots:
                robot.draw(canvas)

            canvas.fill(Color(255))
            canvas.text("Time: %0.1f" % self.time, 10, canvas.height - 10)
