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
import re

from .datasets import get_dataset
from .devices.cameras import Camera
from .devices.rangesensors import RangeSensor
from .hit import Hit
from .utils import Color, Line, Point, distance


class Robot:
    """
    The base robot class.
    """

    def __init__(self, **config):
        self.initialize()
        self.from_json(config)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._devices[item]
        elif isinstance(item, str):
            type_map = {}  # mapping of base to count
            search_groups = re.match(r"(.*)-(\d*)", item)
            if search_groups:
                search_type = search_groups[1].lower()
                search_index = int(search_groups[2])
            else:
                search_type = item.lower()
                search_index = 1
            for device in self._devices:
                # update type_map
                device_type = device.type.lower()
                device_index = None
                if "-" in device_type:
                    device_type, device_index = device_type.rsplit("-", 1)
                    device_index = int(device_index)
                if device_type not in type_map:
                    type_map[device_type] = 1
                else:
                    type_map[device_type] += 1
                if device_index is None:
                    device_index = type_map[device_type]
                if search_type == device_type and search_index == device_index:
                    return device
        return None

    def __repr__(self):
        if self.world is None:
            return "<Robot(name=%r, unconnected)>" % (self.name,)
        else:
            return "<Robot(name=%r, position=%s,%s,%s v=%s,%s,%s)>" % (
                self.name,
                round(self.x, 2),
                round(self.y, 2),
                round(self.direction, 2),
                round(self.vx, 2),
                round(self.vy, 2),
                round(self.va, 2),
            )

    def info(self):
        """
        Get information on a robot.
        """
        if len(self._devices) == 0:
            print("  This robot has no devices.")
        else:
            for i, device in enumerate(self._devices):
                print("      device[%s or %r]: %r" % (i, device.type, device))
            print("  " + ("-" * 25))

    def set_color(self, color):
        """
        Set the color of a robot, and its trace.
        """
        if not isinstance(color, Color):
            self.color = Color(color)
        else:
            self.color = color
        self.trace_color = Color(
            self.color.red * 0.75, self.color.green * 0.75, self.color.blue * 0.75,
        )

    def set_pose(self, x=None, y=None, direction=None):
        """
        Set the pose of the robot. direction is in degrees.
        """
        # Clear the trace
        self.trace[:] = []
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if direction is not None:
            self.direction = direction * math.pi / 180

    def initialize(self):
        """
        Initialize the robot properties.
        """
        self.world = None
        self.name = "Robbie"
        self.state = {}
        self.keep_trace_forever = False
        self.set_color("red")
        self.do_trace = True
        self.trace = []
        self.body = []
        self.max_trace_length = int(1 / 0.1 * 10)  # 10 seconds
        self.x = 0  # cm
        self.y = 0  # cm
        self.height = 0.25
        self.direction = 0  # radians
        self.vx = 0.0  # velocity in x direction, CM per second
        self.vy = 0.0  # velocity in y direction, degrees per second
        self.va = 0.0  # turn velocity
        self.tvx = 0.0
        self.tvy = 0.0
        self.tva = 0.0
        self.va_ramp = 1.0  # seconds to reach max speed
        self.vx_ramp = 1.0  # seconds to reach max speed
        self.vy_ramp = 1.0  # seconds to reach max speed
        self.vx_max = 2.0  # CM/SEC
        self.va_max = math.pi * 0.90  # RADIANS/SEC
        self.vy_max = 2.0  # CM/SEC
        self.stalled = False
        self.bounding_lines = [
            Line(Point(0, 0), Point(0, 0)),
            Line(Point(0, 0), Point(0, 0)),
            Line(Point(0, 0), Point(0, 0)),
            Line(Point(0, 0), Point(0, 0)),
        ]
        self._devices = []
        self.state = {}
        self.image_data = []
        self.get_dataset_image = None
        self.boundingbox = []
        self.radius = 0.0
        self.init_boundingbox()

    def from_json(self, config):
        """
        Load a robot from a JSON config dict.
        """
        if "name" in config:
            self.name = config["name"]

        if "state" in config:
            self.state = config["state"]

        if "do_trace" in config:
            self.do_trace = config["do_trace"]

        if "va" in config:
            self.va = config["va"]
        if "vx" in config:
            self.vx = config["vx"]
        if "vy" in config:
            self.vy = config["vy"]

        if "tva" in config:
            self.tva = config["tva"]
        if "tvx" in config:
            self.tvx = config["tvx"]
        if "tvy" in config:
            self.tvy = config["tvy"]

        if "va_max" in config:
            self.va_max = config["va_max"]
        if "vx_max" in config:
            self.vx_max = config["vx_max"]
        if "vy_max" in config:
            self.vy_max = config["vy_max"]

        if "va_ramp" in config:
            self.va_ramp = config["va_ramp"]
        if "vx_ramp" in config:
            self.vx_ramp = config["vx_ramp"]
        if "vy_ramp" in config:
            self.vy_ramp = config["vy_ramp"]

        if "x" in config:
            self.x = config["x"]
        if "y" in config:
            self.y = config["y"]
        if "direction" in config:
            self.direction = config["direction"] * math.pi / 180

        if "image_data" in config:
            self.image_data = config["image_data"]  # ["dataset", index]
        if len(self.image_data) == 0:
            self.get_dataset_image = None
        else:
            self.get_dataset_image = get_dataset(self.image_data[0])

        if "height" in config:
            self.height = config["height"]  # ratio, 0 to 1 of height

        if "color" in config:
            self.set_color(config["color"])

        if "body" in config:
            self.body[:] = config["body"]
            self.init_boundingbox()

        if "devices" in config:
            for deviceConfig in config["devices"]:
                device = None
                if deviceConfig["class"] == "Camera":
                    device = Camera(**deviceConfig)
                elif deviceConfig["class"] == "RangeSensor":
                    device = RangeSensor(**deviceConfig)
                else:
                    print("Unknown device class:", deviceConfig["class"])

                if device:
                    self.add_device(device)

    def del_device(self, device):
        """
        Remove a device from a robot.
        """
        if isinstance(device, (str, int)):
            device = self[device]
        if device in self._devices:
            device.robot = None
            self._devices.remove(device)
        else:
            print("Device is not on robot.")

    def add_device(self, device):
        """
        Add a device to a robot.
        """
        if device not in self._devices:
            device.robot = self
            self._devices.append(device)
        else:
            print("Can't add the same device to a robot more than once.")

    def to_json(self, robot_list):
        """
        Get this robot as a JSON config file.
        """
        robot_json = {
            "name": self.name,
            "state": self.state,
            "va": self.va,
            "vx": self.vx,
            "vy": self.vy,
            "tva": self.tva,
            "tvx": self.tvx,
            "tvy": self.tvy,
            "va_max": self.va_max,
            "vx_max": self.vx_max,
            "vy_max": self.vy_max,
            "va_ramp": self.va_ramp,
            "vx_ramp": self.vx_ramp,
            "vy_ramp": self.vy_ramp,
            "x": self.x,
            "y": self.y,
            "direction": self.direction * 180 / math.pi,
            "image_data": self.image_data,
            "height": self.height,
            "color": str(self.color),
            "body": self.body,
            "devices": [device.to_json() for device in self._devices],
            "do_trace": self.do_trace,
        }
        return robot_json

    def move(self, translate, rotate):
        """
        Set the target translate and rotate velocities.

        Args should be between -1 and 1.
        """
        # values between -1 and 1
        # compute target velocities
        self.tvx = round(translate * self.vx_max, 1)
        self.tva = round(rotate * self.va_max, 1)

    def forward(self, translate):
        """
        Set the target translate velocity.

        Arg should be between -1 and 1.
        """
        # values between -1 and 1
        self.tvx = round(translate * self.vx_max, 1)

    def backward(self, translate):
        """
        Set the target translate velocity.

        Arg should be between -1 and 1.
        """
        # values between -1 and 1
        self.tvx = round(-translate * self.vx_max, 1)

    def reverse(self):
        """
        Flip the target x velocity from negative to
        positive or from positive to negative.
        """
        self.tvx = -self.tvx

    def turn(self, rotate):
        """
        Set the target rotate velocity.

        Arg should be between -1 and 1.
        """
        # values between -1 and 1
        self.tva = rotate * self.va_max

    def stop(self):
        """
        Set the target velocities to zeros.
        """
        self.tvx = 0.0
        self.tvy = 0.0
        self.tva = 0.0

    def ccw(self, ax, ay, bx, by, cx, cy):
        # counter clockwise
        return ((cy - ay) * (bx - ax)) > ((by - ay) * (cx - ax))

    def intersect(self, ax, ay, bx, by, cx, cy, dx, dy):
        # Return true if line segments AB and CD intersect
        return self.ccw(ax, ay, cx, cy, dx, dy) != self.ccw(
            bx, by, cx, cy, dx, dy
        ) and (self.ccw(ax, ay, bx, by, cx, cy) != self.ccw(ax, ay, bx, by, dx, dy))

    def coefs(self, p1x, p1y, p2x, p2y):
        A = p1y - p2y
        B = p2x - p1x
        C = p1x * p2y - p2x * p1y
        return [A, B, -C]

    def intersect_coefs(self, L1_0, L1_1, L1_2, L2_0, L2_1, L2_2):
        D = L1_0 * L2_1 - L1_1 * L2_0
        if D != 0:
            Dx = L1_2 * L2_1 - L1_1 * L2_2
            Dy = L1_0 * L2_2 - L1_2 * L2_0
            x1 = Dx / D
            y1 = Dy / D
            return [x1, y1]
        else:
            return None

    def intersect_hit(self, p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y):
        """
        Compute the intersection between two lines.
        """
        # http:##stackoverflow.com/questions/20677795/find-the-point-of-intersecting-lines
        L1 = self.coefs(p1x, p1y, p2x, p2y)
        L2 = self.coefs(p3x, p3y, p4x, p4y)
        xy = self.intersect_coefs(L1[0], L1[1], L1[2], L2[0], L2[1], L2[2])
        # now check to see on both segments:
        if xy:
            lowx = min(p1x, p2x) - 0.1
            highx = max(p1x, p2x) + 0.1
            lowy = min(p1y, p2y) - 0.1
            highy = max(p1y, p2y) + 0.1
            if (lowx <= xy[0] and xy[0] <= highx) and (
                lowy <= xy[1] and xy[1] <= highy
            ):
                lowx = min(p3x, p4x) - 0.1
                highx = max(p3x, p4x) + 0.1
                lowy = min(p3y, p4y) - 0.1
                highy = max(p3y, p4y) + 0.1
                if (
                    lowx <= xy[0]
                    and xy[0] <= highx
                    and lowy <= xy[1]
                    and xy[1] <= highy
                ):
                    return xy

        return None

    def has_image(self):
        """
        Does this robot have an associated 3D set of images from
        a dataset?
        """
        return self.get_dataset_image is not None

    def get_image(self, degrees):
        """
        Return the 3D image in the proper angle.
        """
        return self.get_dataset_image(self.image_data[1], degrees)

    def cast_ray(self, x1, y1, a, maxRange):
        """
        Cast a ray into this world and see what it hits.
        """
        # walls and robots
        hits = []
        x2 = math.sin(a) * maxRange + x1
        y2 = math.cos(a) * maxRange + y1

        for wall in self.world.walls:
            # never detect hit with yourself
            if wall.robot is self:
                continue
            for line in wall.lines:
                p1 = line.p1
                p2 = line.p2
                pos = self.intersect_hit(x1, y1, x2, y2, p1.x, p1.y, p2.x, p2.y)
                if pos is not None:
                    dist = distance(pos[0], pos[1], x1, y1)
                    height = 1.0 if wall.robot is None else wall.robot.height
                    color = wall.robot.color if wall.robot else wall.color
                    hits.append(
                        Hit(wall.robot, height, pos[0], pos[1], dist, color, x1, y1)
                    )

        hits.sort(
            key=lambda a: a.distance, reverse=True
        )  # further away first, back to front
        return hits

    def init_boundingbox(self):
        # First, find min/max points around robot (assumes box):
        min_x = float("inf")
        max_x = float("-inf")
        min_y = float("inf")
        max_y = float("-inf")
        max_dist = float("-inf")

        if len(self.body) > 0 and self.body[0][0] == "polygon":
            # "polygon", color, points
            for point in self.body[0][2]:
                min_x = min(min_x, point[0])
                min_y = min(min_y, point[1])
                max_x = max(max_x, point[0])
                max_y = max(max_y, point[1])
                max_dist = max(max_dist, distance(0, 0, point[0], point[1]))

        if (
            min_x == float("inf")
            or min_y == float("inf")
            or max_x == float("-inf")
            or max_y == float("-inf")
        ):
            return

        self.boundingbox = [min_x, min_y, max_x, max_y]
        self.radius = max_dist
        ps = self.compute_boundingbox(self.x, self.y, self.direction)
        self.update_boundingbox(*ps)

    def compute_boundingbox(self, px, py, pdirection):
        # Compute position in real world with respect to x, y, direction:
        min_x, min_y, max_x, max_y = self.boundingbox
        ps = []
        for x, y in [
            (min_x, max_y),  # 4
            (min_x, min_y),  # 1
            (max_x, min_y),  # 2
            (max_x, max_y),  # 3
        ]:
            dist = distance(0, 0, x, y)
            angle = math.atan2(-x, y)
            p = self.rotate_around(px, py, dist, pdirection + angle + math.pi / 2)
            ps.append(p)
        return ps

    def restore_boundingbox(self):
        self.update_boundingbox(*self.last_boundingbox)

    def update_boundingbox(self, p1, p2, p3, p4):
        self.last_boundingbox = [
            self.bounding_lines[0].p1.copy(),  # p1
            self.bounding_lines[0].p2.copy(),  # p2
            self.bounding_lines[1].p2.copy(),  # p3
            self.bounding_lines[2].p2.copy(),  # p4
        ]
        self.bounding_lines[0].p1.x = p1[0]
        self.bounding_lines[0].p1.y = p1[1]
        self.bounding_lines[0].p2.x = p2[0]
        self.bounding_lines[0].p2.y = p2[1]

        self.bounding_lines[1].p1.x = p2[0]
        self.bounding_lines[1].p1.y = p2[1]
        self.bounding_lines[1].p2.x = p3[0]
        self.bounding_lines[1].p2.y = p3[1]

        self.bounding_lines[2].p1.x = p3[0]
        self.bounding_lines[2].p1.y = p3[1]
        self.bounding_lines[2].p2.x = p4[0]
        self.bounding_lines[2].p2.y = p4[1]

        self.bounding_lines[3].p1.x = p4[0]
        self.bounding_lines[3].p1.y = p4[1]
        self.bounding_lines[3].p2.x = p1[0]
        self.bounding_lines[3].p2.y = p1[1]

    def _deltav(self, tv, v, maxv, ramp, time_step):
        # max change occurs in how long:
        seconds = ramp
        # how much can we change in one time step?
        spt = seconds / time_step
        dv = maxv / spt  # change in one time step
        return min(max(tv - v, -dv), dv)  # keep in limit

    def step(self, time_step):
        """
        Have the robot make one step in time. Check to see if it hits
        any obstacles.
        """
        # proposed acceleration:
        va = self.va + self._deltav(
            self.tva, self.va, self.va_max, self.va_ramp, time_step
        )
        vx = self.vx + self._deltav(
            self.tvx, self.vx, self.vx_max, self.vx_ramp, time_step
        )
        vy = self.vy + self._deltav(
            self.tvy, self.vy, self.vy_max, self.vy_ramp, time_step
        )
        # graphics offset:
        offset = math.pi / 2
        # proposed positions:
        pdirection = self.direction - va * time_step
        tvx = (
            vx * math.sin(-pdirection + offset)
            + vy * math.cos(-pdirection + offset) * time_step
        )
        tvy = (
            vx * math.cos(-pdirection + offset)
            - vy * math.sin(-pdirection + offset) * time_step
        )
        px = self.x + tvx
        py = self.y + tvy

        # check to see if collision
        # bounding box:
        p1, p2, p3, p4 = self.compute_boundingbox(px, py, pdirection)
        # Set wall bounding boxes for collision detection:
        self.update_boundingbox(p1, p2, p3, p4)

        self.stalled = False
        # if intersection, can't move:
        for wall in self.world.walls:
            if wall.robot is self:  # if yourself, don't check for collision
                continue
            for line in wall.lines:
                w1 = line.p1
                w2 = line.p2
                if (
                    self.intersect(p1[0], p1[1], p2[0], p2[1], w1.x, w1.y, w2.x, w2.y)
                    or self.intersect(
                        p2[0], p2[1], p3[0], p3[1], w1.x, w1.y, w2.x, w2.y
                    )
                    or self.intersect(
                        p3[0], p3[1], p4[0], p4[1], w1.x, w1.y, w2.x, w2.y
                    )
                    or self.intersect(
                        p4[0], p4[1], p1[0], p1[1], w1.x, w1.y, w2.x, w2.y
                    )
                ):
                    self.stalled = True
                    break

        if not self.stalled:
            # if no intersection, make move
            self.va = va
            self.vx = vx
            self.vy = vy
            self.x = px
            self.y = py
            self.direction = pdirection
        else:
            self.restore_boundingbox()
            # Adjust actual velocity
            self.va = 0
            self.vx = 0
            self.vy = 0

        if self.do_trace:
            self.trace.append((Point(self.x, self.y), self.direction))

        # Devices:
        for device in self._devices:
            device.step(time_step)

    def update(self, debug_list=None):
        """
        Update the robot, and devices.
        """
        self.init_boundingbox()
        if debug_list is not None:
            debug_list.append(("strokeStyle", (Color(255), 1)))
            debug_list.append(
                (
                    "draw_line",
                    (
                        self.bounding_lines[0].p1.x,
                        self.bounding_lines[0].p1.y,
                        self.bounding_lines[0].p2.x,
                        self.bounding_lines[0].p2.y,
                    ),
                )
            )

            debug_list.append(
                (
                    "draw_line",
                    (
                        self.bounding_lines[1].p1.x,
                        self.bounding_lines[1].p1.y,
                        self.bounding_lines[1].p2.x,
                        self.bounding_lines[1].p2.y,
                    ),
                )
            )

            debug_list.append(
                (
                    "draw_line",
                    (
                        self.bounding_lines[2].p1.x,
                        self.bounding_lines[2].p1.y,
                        self.bounding_lines[2].p2.x,
                        self.bounding_lines[2].p2.y,
                    ),
                )
            )

            debug_list.append(
                (
                    "draw_line",
                    (
                        self.bounding_lines[3].p1.x,
                        self.bounding_lines[3].p1.y,
                        self.bounding_lines[3].p2.x,
                        self.bounding_lines[3].p2.y,
                    ),
                )
            )

        # Devices:
        for device in self._devices:
            device.update(debug_list)
        return

    def rotate_around(self, x1, y1, length, angle):
        """
        Swing a line around a point.
        """
        return [x1 + length * math.cos(-angle), y1 - length * math.sin(-angle)]

    def draw(self, backend):
        """
        Draw the robot.
        """
        if self.do_trace:
            backend.draw_lines(
                [
                    (point[0], point[1])
                    for (point, direction) in self.trace[-self.max_trace_length :]
                ],
                stroke_style=self.trace_color,
            )
            if not self.keep_trace_forever:
                self.trace = self.trace[-self.max_trace_length :]

        backend.pushMatrix()
        backend.translate(self.x, self.y)
        backend.rotate(self.direction)

        # body:

        for shape in self.body:
            shape_name, color, args = shape

            if self.stalled:
                backend.set_fill(Color(128, 128, 128))
                backend.strokeStyle(Color(255), 1)
            elif color is None:
                backend.set_fill(self.color)
                backend.noStroke()
            else:
                backend.set_fill(Color(color))
                backend.noStroke()

            if shape_name == "polygon":
                backend.beginShape()
                for x, y in args:
                    backend.vertex(x, y)
                backend.endShape()
                backend.noStroke()
            elif shape_name == "rectangle":
                backend.draw_rect(*args)

        for device in self._devices:
            device.draw(backend)

        backend.popMatrix()


SCRIBBLER_CONFIG = {
    "body": [
        [
            "polygon",
            None,
            [
                [4.17, 5],
                [4.17, 6.67],
                [5.83, 5.83],
                [5.83, 5],
                [7.5, 5],
                [7.5, -5],
                [5.83, -5],
                [5.83, -5.83],
                [4.17, -6.67],
                [4.17, -5],
                [-4.17, -5],
                [-4.17, -6.67],
                [-5.83, -5.83],
                [-6.67, -5],
                [-7.5, -4.17],
                [-7.5, 4.17],
                [-6.67, 5],
                [-5.83, 5.83],
                [-4.17, 6.67],
                [-4.17, 5],
            ],
        ],
        ["rectangle", "black", [-3.33, -7.67, 6.33, 1.67]],
        ["rectangle", "black", [-3.33, 6, 6.33, 1.67]],
    ],
    "color": "#FF0000FF",
    "name": "Scribbie",
}


class Scribbler(Robot):
    def __init__(self, **config):
        defaults = SCRIBBLER_CONFIG.copy()
        defaults.update(config)
        super().__init__(**defaults)
