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
import re
import signal
import sys
import time
from contextlib import contextmanager
from numbers import Number

from .backends import make_backend
from .robot import Robot
from .utils import distance  # noqa
from .utils import Color, Line, Point, distance_point_to_line, json_dump

DEFAULT_HANDLER = signal.getsignal(signal.SIGINT)


class Wall:
    """
    Class representing obstacles in the world. If the bounding box of
    a robot, then robot will be that robot, else None.
    """

    def __init__(self, color, robot, *lines):
        self.color = color
        self.robot = robot
        self.lines = lines

    def __repr__(self):
        return "Wall(%r, %r, %r)" % (self.color, self.robot, self.lines)


class World:
    """
    The Jyrobot simulator world.
    """

    def __init__(self, **config):
        """
        Takes a world JSON config dict (as **) or
        any keyword from the config.
        """
        # For faster-than real time display with synchronous backends,
        # keep processing time below this percentage of throttle_period:
        self.show_throttle_percentage = 0.40
        self.time_decimal_places = 1
        self.throttle_period = 0.1
        self.time_of_last_call = 0
        self.debug = False
        self.debug_list = []
        self._robots = []
        self.backend = None
        self.config = config.copy()
        self.init()  # default values
        self.reset()  # from config

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._robots[item]
        elif isinstance(item, str):
            name_map = {}  # mapping of base to count
            search_groups = re.match(r"(.*)-(\d*)", item)
            if search_groups:
                search_name = search_groups[1].lower()
                search_index = int(search_groups[2])
            else:
                search_name = item.lower()
                search_index = 1
            for robot in self._robots:
                # update name_map
                robot_name = robot.name.lower()
                robot_index = None
                if "-" in robot_name:
                    robot_name, robot_index = robot_name.rsplit("-", 1)
                    robot_index = int(robot_index)
                if robot_name not in name_map:
                    name_map[robot_name] = 1
                else:
                    name_map[robot_name] += 1
                if robot_index is None:
                    robot_index = name_map[robot_name]
                if search_name == robot_name and search_index == robot_index:
                    return robot

        return None

    def __len__(self):
        return len(self._robots)

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
        """
        Take a picture of the world, or of a robot.
        """
        # Make sure it is up to date
        self.update(show=False)
        self.draw()  # force
        if self.backend.is_async():
            # wait for backend to updatea
            time.sleep(self.throttle_period)
        try:
            picture = self.backend.take_picture()
        except RuntimeError:
            print("Backend is not ready yet; try again")
            return

        if picture is None:
            return

        if index is not None:
            robot = self[index]
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
        """
        Get info about this world, and all of its robots.
        """
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
        """
        Switch graphic backends. Valid choices are:
            * "jupyter"
            * "svg"
            * "debug"
        """
        self.backend = make_backend(self.width, self.height, self.scale)
        self.backend.update_dimensions(self.width, self.height, self.scale)

    def init(self):
        """
        Sets the default values.
        """
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
        self.complexity = 0
        if len(self._robots) > 0:
            print("Removing robots from world...")
            for robot in self._robots:
                robot.world = None
        self._robots = []

    def reset(self):
        """
        Reloads the config from initialization, or from
        last save.
        """
        self.init()
        self.from_json(self.config)
        self.update(show=False)  # twice to allow robots to see each other
        self.update(show=False)
        self.draw()  # force

    def set_seed(self, seed):
        """
        Set the random seed.
        """
        random.seed(seed)
        self.seed = seed
        self.config["seed"] = seed

    def from_json(self, config):
        """
        Load a json config file.
        """
        self.config = config
        if "seed" not in config or config["seed"] == 0:
            seed = random.randint(0, sys.maxsize)
            print("Random seed initialized to:", seed)
        else:
            seed = config["seed"]
            print("Reusing random seed:", seed)
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
        """
        Remove any boundary walls.
        """
        self.walls[:] = [wall for wall in self.walls if len(wall.lines) > 1]
        self.complexity = self.compute_complexity()

    def add_boundary_walls(self):
        """
        Add boundary walls around world.
        """
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
            self.complexity = self.compute_complexity()

    def to_json(self):
        """
        Get the world as a JSON dict.
        """
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
        """
        Save the current state of the world as the config, and
        save it back to disc if it was loaded from disk.
        """
        # First, save internally.
        self.config = self.to_json()
        if self.filename is not None and os.path.exists(self.filename):
            with open(self.filename, "w") as fp:
                json_dump(self.config, fp, sort_keys=True, indent=4)
        else:
            print("Saved in memory. Use world.save_as('filename') to save to disk.")

    def save_as(self, filename):
        """
        Save the world config JSON as a new file.
        """
        if not filename.endswith(".json"):
            filename = filename + ".json"
        # First, save internally.
        self.config = self.to_json()
        with open(filename, "w") as fp:
            json_dump(self.to_json(), fp, sort_keys=True, indent=4)
        self.config["filename"] = filename
        # Now you can use save():

    def set_scale(self, scale):
        """
        Change the scale of the rendered world.
        """
        self.scale = scale
        self.backend.update_dimensions(self.width, self.height, self.scale)
        # Save with config
        self.config["scale"] = self.scale
        self.update(show=False)
        self.draw()  # force

    def gallery(self, *images, border_width=1, background_color=(255, 255, 255)):
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
        """
        Display the objects in a notebook, jupyter lab, or regular python.
        """
        try:
            from PIL import Image
        except ImportError:
            Image = None

        try:
            from IPython.display import clear_output, display
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
        """
        Create a live view to the simulator.
        """
        self.backend.watch(*args, **kwargs)
        # Two updates to force all robots to see each other
        self.update(show=False)
        self.update(show=False)
        self.draw()  # force

    def add_wall(self, color, x1, y1, x2, y2):
        """
        Add a box of walls.
        """
        p1 = Point(x1, y1)
        p2 = Point(x2, y1)
        p3 = Point(x2, y2)
        p4 = Point(x1, y2)
        ## Pairs of points make Line:
        wall = Wall(
            Color(color), None, Line(p1, p2), Line(p2, p3), Line(p3, p4), Line(p4, p1)
        )
        self.walls.append(wall)
        self.complexity = self.compute_complexity()
        self.update(show=True)

    def del_robot(self, robot):
        """
        Removed a robot from the world.
        """
        if not isinstance(robot, Robot):
            # Then look it up by index/name/type:
            robot = self[robot]
        for wall in list(self.walls):
            if wall.robot is robot:
                self.walls.remove(wall)
        if robot in self._robots:
            robot.world = None
            self._robots.remove(robot)
        self.complexity = self.compute_complexity()
        self.update(show=True)

    def add_robot_randomly(self, robot):
        """
        Add a robot to the world in a random position.
        """
        # TODO: avoid walls too
        pa = random.random() * math.pi * 2
        for i in range(100):
            too_close = False
            px = round(robot.radius + random.random() * (self.width - 2 * robot.radius))
            py = round(
                robot.radius + random.random() * (self.height - 2 * robot.radius)
            )
            for other in self:
                if distance(px, py, other.x, other.y) < robot.radius + other.radius:
                    too_close = True
                    break

            for wall in self.walls:
                for line in wall.lines:
                    dist, location = distance_point_to_line((px, py), line.p1, line.p2)
                    if dist < robot.radius:
                        too_close = True
                        break
            if not too_close:
                return px, py, pa

        raise Exception("Couldn't find a place for robot after 100 tries; giving up")

    def add_robot(self, robot):
        """
        Add a new robot to the world.
        """
        if robot not in self._robots:
            if robot.x == 0 and robot.y == 0:
                robot.x, robot.y, robot.direction = self.add_robot_randomly(robot)
            self._robots.append(robot)
            robot.world = self
            # Bounding lines form a wall:
            wall = Wall(robot.color, robot, *robot.bounding_lines)
            self.walls.append(wall)
            self.complexity = self.compute_complexity()
            self.update(show=True)
        else:
            print("Can't add the same robot to a world more than once.")

    def signal_handler(self, *args, **kwargs):
        """
        Handler for Control+C.
        """
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
        """
        Run the simulator until one of the control functions returns True
        or Control+C is pressed.

        Args:
            function - (optional) either a single function that takes the
                world, or a list of functions (or None) that each take
                a robot. If any function returns True, then simulation will
                stop.

        """
        time_step = time_step if time_step is not None else self.time_step
        self.steps(sys.maxsize, function, time_step, show, real_time)

    def seconds(
        self, seconds=5.0, function=None, time_step=None, show=True, real_time=True
    ):
        """
        Run the simulator for N seconds, or until one of the control
        functions returns True or Control+C is pressed.

        Args:
            function - (optional) either a single function that takes the
                world, or a list of functions (or None) that each take
                a robot. If any function returns True, then simulation will
                stop.
        """
        time_step = time_step if time_step is not None else self.time_step
        count = round(seconds / time_step)
        self.steps(count, function, time_step, show, real_time)

    def steps(self, steps=1, function=None, time_step=None, show=True, real_time=True):
        """
        Run the simulator for N steps, or until one of the control
        functions returns True or Control+C is pressed.

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
                self.step(time_step, show=show, real_time=real_time)

        stop_real_time = time.monotonic()
        stop_time = self.time
        speed = (stop_time - start_time) / (stop_real_time - start_real_time)
        print(
            "Simulation stopped at: %s; speed %s x real time"
            % (self.formatted_time(), round(speed, 2))
        )
        self.update(show=False)  # get updates
        self.draw()  # force to update any displays

    def compute_complexity(self):
        # Proxy for how much drawing
        return sum([len(wall.lines) for wall in self.walls])

    def step(self, time_step=None, show=True, real_time=True):
        """
        Run the simulator for 1 step.

        Args:
        """
        if not isinstance(time_step, Number):
            raise ValueError("Invalid time_step: %r; should be a number" % time_step)
        if not isinstance(show, bool):
            raise ValueError("Invalid show: %r; should be a bool" % show)
        if not isinstance(real_time, bool):
            raise ValueError("Invalid real_time: %r; should be a bool" % real_time)

        # Throttle needs to take into account the async update time
        # So as not to overwhelm the system. We give 0.1 time
        # per robot. This can be optimized to reduce the load.

        if self.backend.is_async():
            self.throttle_period = self.backend.get_dynamic_throttle(self)

        time_step = time_step if time_step is not None else self.time_step
        start_time = time.monotonic()
        for robot in self._robots:
            robot.step(time_step)
        self.time += time_step
        self.time = round(self.time, self.time_decimal_places)
        self.update(show)
        if show:
            now = time.monotonic()
            time_passed = now - start_time
            if real_time:  # real_time is ignored if not show
                sleep_time = self.time_step - time_passed
                # Tries to sleep enough to make even with real time/throttle time:
                # If running faster than real time/throttle period, need to wait some
                if sleep_time >= 0:
                    # Sleep even more for slow-motion:
                    time.sleep(sleep_time)
                # else it is already running slower than real time
            elif not self.backend.is_async():
                # Goal is to keep time_passed less than % of throttle period:
                if time_passed > self.throttle_period * self.show_throttle_percentage:
                    self.throttle_period += time_step

    def update(self, show=True):
        """
        Update the world, robots, and devices. Optionally, draw the
        world.
        """
        ## Update robots:
        # None, or a list
        self.debug_list = [] if self.debug else None
        for robot in self._robots:
            robot.update(self.debug_list)
        if show:
            self.request_draw()

    def request_draw(self):
        """
        Draw the world. This function is throttled
        """
        # Throttle:
        now = time.monotonic()
        time_since_last_call = now - self.time_of_last_call

        if time_since_last_call > self.throttle_period:
            self.time_of_last_call = now
            # End of throttle code

            self.draw()  # force

    def draw(self):
        """
        Force a redraw of the world.
        """
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

            if self.debug_list:
                for command, args in self.debug_list:
                    self.backend.do_command(command, *args)

        self.backend.update_watchers()
