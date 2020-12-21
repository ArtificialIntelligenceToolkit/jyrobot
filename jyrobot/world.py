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
import os
import random
import signal
import sys
import time
from contextlib import contextmanager

from .backends import make_backend
from .robot import Robot
from .utils import Color, Line, Point, json_dump, throttle

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
        return repr(self.world._robots)


class World:
    def __init__(self, **config):
        self.debug = False
        self._robots = []
        self.robot = Robots(self)
        self.backend = None
        self.config = config.copy()
        self.init()  # default values
        self.reset()  # from config
        self.update()
        self.update()
        self.force_draw()

    def __repr__(self):
        return "<World width=%r, height=%r>" % (self.width, self.height)

    def _repr_png_(self):
        image = self.take_picture()
        if image:
            return image._repr_png_()
        return

    def formatted_time(self):
        hours = self.time // 3600
        minutes = (self.time % 3600) // 60
        seconds = (self.time % 3600) % 60
        return "%02d:%02d:%04.1f" % (hours, minutes, seconds)

    def take_picture(self, index=None, size=100):
        # Make sure it is up to date
        self.update()
        self.draw()
        try:
            picture = self.backend.take_picture()
        except RuntimeError:
            print("Backend is not ready yet; try again")
            return

        if picture is None:
            return

        if index is not None:
            robot = self.robot[index]
            if robot:
                start_x = round(max(robot.x * self.scale - size / 2, 0))
                start_y = round(max(robot.y * self.scale - size / 2, 0))
                rectangle = (
                    start_x,
                    start_y,
                    min(start_x + size, self.width * self.scale),
                    min(start_y + size, self.height * self.scale),
                )
                picture = picture.crop(rectangle)
                return picture
        else:
            return picture

    def info(self):
        if self.filename:
            print("This world was loaded from %r" % self.filename)
        if len(self._robots) == 0:
            print("This world has no robots.")
        else:
            print("Robots:")
            print("-" * 25)
            for i, robot in enumerate(self._robots):
                print("  robot[%s or %r]: %r" % (i, robot.name, robot))
                robot.info()

    def switch_backend(self, backend):
        self.backend = make_backend(self.width, self.height, self.scale)
        self.backend.update_dimensions(self.width, self.height, self.scale)

    def init(self):
        self.filename = None
        self.seed = 0
        self.width = 500
        self.height = 250
        self.scale = 3.0
        self.stop = False  # should stop?
        self.time_step = 0.10  # seconds
        self.time = 0.0  # seconds
        self.boundary_wall = True
        self.boundary_wall_width = 1
        self.boundary_wall_color = Color(128, 0, 128)
        self.ground_color = Color(0, 128, 0)
        self.walls = []
        if len(self._robots) > 0:
            print("Removing robots from world...")
            for robot in self._robots:
                robot.world = None
        self._robots = []

    def reset(self):
        self.init()
        self.from_json(self.config)
        self.force_draw()

    def set_seed(self, seed):
        random.seed(seed)
        self.seed = seed

    def from_json(self, config):
        self.config = config
        if "seed" not in config or config["seed"] == 0:
            seed = random.randint(0, sys.maxsize)
            print("Random seed initialized to:", seed)
        else:
            seed = config["seed"]
            print("Reusing random seed:", self.seed)
        self.set_seed(seed)

        if "filename" in config:
            self.filename = config["filename"]
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

        self.add_boundary_walls()

        for wall in config.get("walls", []):
            # Walls are "boxes"... 4 lines:
            self.add_wall(
                wall["color"],
                wall["p1"]["x"],
                wall["p1"]["y"],
                wall["p2"]["x"],
                wall["p2"]["y"],
            )
        ## Create robot, and add to world:
        for robotConfig in self.config.get("robots", []):
            robot = Robot(**robotConfig)
            self.add_robot(robot)
        # Create the backend if first time:
        if self.backend is None:
            self.backend = make_backend(self.width, self.height, self.scale)
        # Update the backend if it already existed, but differs in config
        self.backend.update_dimensions(self.width, self.height, self.scale)

    def clear_boundary_walls(self):
        self.walls[:] = [wall for wall in self.walls if len(wall.lines) > 1]

    def add_boundary_walls(self):
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

    def to_json(self):
        config = {
            "seed": self.seed,
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
        # First, save internally.
        self.config = self.to_json()
        if self.filename is not None and os.path.exists(self.filename):
            with open(self.filename, "w") as fp:
                json_dump(self.config, fp, sort_keys=True, indent=4)
        else:
            print("Saved in memory. Use world.save_as('filename') to save to disk.")

    def save_as(self, filename):
        # First, save internally.
        self.config = self.to_json()
        with open(filename, "w") as fp:
            json_dump(self.to_json(), fp, sort_keys=True, indent=4)

    def set_scale(self, scale):
        self.scale = scale
        self.backend.change_scale(self.scale)
        # Save with config
        self.config["scale"] = self.scale
        self.force_draw()

    def gallery(self, *images, border_width=1, background_color=(0, 0, 0)):
        """
        Construct a gallery of images
        """
        try:
            from PIL import Image
        except ImportError:
            print("world.gallery() requires Pillow, Python Image Library (PIL)")
            return

        gallery_cols = math.ceil(math.sqrt(len(images)))
        gallery_rows = math.ceil(len(images) / gallery_cols)

        size = images[0].size
        size = size[0] + (border_width * 2), size[1] + (border_width * 2)

        gallery_image = Image.new(
            mode="RGBA",
            size=(int(gallery_cols * size[0]), int(gallery_rows * size[1])),
            color=background_color,
        )

        for i, image in enumerate(images):
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            location = (
                int((i % gallery_cols) * size[0]) + border_width,
                int((i // gallery_cols) * size[1]) + border_width,
            )
            gallery_image.paste(image, location)
        return gallery_image

    def display(self, *objects, **kwargs):
        try:
            from PIL import Image
        except ImportError:
            Image = None

        try:
            from IPython.display import display, clear_output
        except ImportError:

            def clear_output(wait=None):
                pass

            display = print

        wait = kwargs.pop("wait", True)

        if Image is not None:
            if (
                all([isinstance(obj, Image.Image) for obj in objects])
                and len(objects) > 1
            ):
                objects = [self.gallery(*objects, **kwargs)]

        clear_output(wait=wait)
        display(*objects)

    def watch(self, *args, **kwargs):
        self.backend.watch(*args, **kwargs)
        # Two updates to force all robots to see each other
        self.update()
        self.update()
        self.force_draw()

    def add_wall(self, color, x1, y1, x2, y2):
        p1 = Point(x1, y1)
        p2 = Point(x2, y1)
        p3 = Point(x2, y2)
        p4 = Point(x1, y2)
        ## Pairs of points make Line:
        wall = Wall(
            Color(color), None, Line(p1, p2), Line(p2, p3), Line(p3, p4), Line(p4, p1)
        )
        self.walls.append(wall)
        self.update(show=False)
        self.force_draw()

    def del_robot(self, robot):
        for wall in list(self.walls):
            if wall.robot is robot:
                self.walls.remove(wall)
        if robot in self._robots:
            robot.world = None
            self._robots.remove(robot)
        self.update(show=False)
        self.force_draw()

    def add_robot(self, robot):
        if robot not in self._robots:
            if robot.x == 0:
                robot.x = round(random.random() * (self.width - 10))
            if robot.y == 0:
                robot.y = round(random.random() * (self.height - 10))
            self._robots.append(robot)
            robot.world = self
            # Bounding lines form a wall:
            wall = Wall(robot.color, robot, *robot.bounding_lines)
            self.walls.append(wall)
            self.update(show=False)
            self.force_draw()
        else:
            print("Can't add the same robot to a world more than once.")

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

    def run(self, function=None, time_step=None, show=True, real_time=True):
        time_step = time_step if time_step is not None else self.time_step
        self.steps(sys.maxsize, function, time_step, show, real_time)

    def seconds(
        self, seconds=5.0, function=None, time_step=None, show=True, real_time=True
    ):
        time_step = time_step if time_step is not None else self.time_step
        count = round(seconds / time_step)
        self.steps(count, function, time_step, show, real_time)

    def steps(self, steps=1, function=None, time_step=None, show=True, real_time=True):
        """
        Args:
            function - (optional) either a single function that takes the
                world, or a list of functions (or None) that each take
                a robot. If any function returns True, then simulation will
                stop.
        """
        time_step = time_step if time_step is not None else self.time_step
        with self.no_interrupt():
            start_real_time = time.monotonic()
            start_time = self.time
            for step in range(steps):
                if self.stop:
                    break
                self.step(time_step, show=show, real_time=real_time)
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
                        break
            stop_real_time = time.monotonic()
            stop_time = self.time
            speed = (stop_time - start_time) / (stop_real_time - start_real_time)
        print(
            "Simulation stopped at: %s; speed %s x real time"
            % (self.formatted_time(), round(speed, 2))
        )

    def step(self, time_step=None, show=True, real_time=True):
        extra_sleep = 0
        time_step = time_step if time_step is not None else self.time_step
        start_time = time.monotonic()
        for robot in self._robots:
            robot.step(time_step)
        self.time += time_step
        self.update(show)
        if show and real_time:  # real_time is ignored if not show
            now = time.monotonic()
            # Tries to sleep enough to make even with real time:
            sleep_time = time_step - (now - start_time)
            if sleep_time >= 0:
                # Sleep even more for slow-motion:
                time.sleep(sleep_time + extra_sleep)
            else:
                extra_sleep += abs(sleep_time)

    def update(self, show=True):
        ## Update robots:
        # None, or a list
        debug_list = [] if self.debug else None
        for robot in self._robots:
            robot.update(debug_list)
        if show:
            self.draw(debug_list)

    @throttle(0.1)
    def draw(self, debug_list=[]):
        self.force_draw(debug_list)

    def force_draw(self, debug_list=[]):
        if self.backend is None:
            return

        with self.backend:
            self.backend.clear()
            self.backend.noStroke()
            self.backend.set_fill(self.ground_color)
            self.backend.draw_rect(0, 0, self.width, self.height)
            ## Draw walls:
            for wall in self.walls:
                if len(wall.lines) >= 1 and wall.robot is None:
                    c = wall.color
                    self.backend.noStroke()
                    self.backend.set_fill(c)
                    self.backend.beginShape()
                    for line in wall.lines:
                        self.backend.vertex(line.p1.x, line.p1.y)
                        self.backend.vertex(line.p2.x, line.p2.y)

                    self.backend.endShape()

            ## Draw borders:
            for wall in self.walls:
                c = wall.color
                if len(wall.lines) == 1:
                    self.backend.strokeStyle(c, 3)
                    self.backend.draw_line(
                        wall.lines[0].p1.x,
                        wall.lines[0].p1.y,
                        wall.lines[0].p2.x,
                        wall.lines[0].p2.y,
                    )
                    self.backend.lineWidth(1)
                    self.backend.noStroke()

            ## Draw robots:
            for robot in self._robots:
                robot.draw(self.backend)

            self.backend.set_fill(Color(255))
            self.backend.text(self.formatted_time(), 10, self.height - 10)

            if debug_list:
                for command, args in debug_list:
                    self.backend.do_command(command, *args)
