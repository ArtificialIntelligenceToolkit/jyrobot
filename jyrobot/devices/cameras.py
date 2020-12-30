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

from ..utils import Color


class Camera:
    """
    A camera device.
    """

    def __init__(self, **config):
        self.type = "camera"
        self.time = 0.0
        self.robot = None
        self.cameraShape = [256, 128]
        # 0 = no fade, 1.0 = max fade
        self.colorsFadeWithDistance = 0.5
        self.sizeFadeWithDistance = 1.0
        self.reflectGround = True
        self.reflectSky = False
        self.set_fov(60)  # degrees
        self.reset()

    def __repr__(self):
        return "<Camera size=(%r,%r), angle=%r>" % (
            self.cameraShape[0],
            self.cameraShape[1],
            round(self.angle * 180 / math.pi, 2),
        )

    def watch(self):
        from ..widgets import CameraWatcher

        watcher = CameraWatcher(self)
        self.robot.watchers.append(watcher)
        # Return the widget:
        return watcher.widget

    def from_json(self, config):
        if "width" in config:
            self.cameraShape[0] = config["width"]
        if "height" in config:
            self.cameraShape[1] = config["height"]

        if "colorsFadeWithDistance" in config:
            self.colorsFadeWithDistance = config["colorsFadeWithDistance"]
        if "sizeFadeWithDistance" in config:
            self.sizeFadeWithDistance = config["sizeFadeWithDistance"]
        if "reflectGround" in config:
            self.reflectGround = config["reflectGround"]
        if "reflectSky" in config:
            self.reflectSky = config["reflectSky"]
        if "angle" in config:
            self.set_fov(config["angle"])  # degrees

    def to_json(self):
        return {
            "class": self.__class__.__name__,
            "width": self.cameraShape[0],
            "height": self.cameraShape[1],
            "colorsFadeWithDistance": self.colorsFadeWithDistance,
            "sizeFadeWithDistance": self.sizeFadeWithDistance,
            "reflectGround": self.reflectGround,
            "reflectSky": self.reflectSky,
            "angle": self.angle * 180 / math.pi,  # save in degrees
        }

    def reset(self):
        self.hits = [[] for i in range(self.cameraShape[0])]

    def step(self, time_step):
        pass

    def set_fov(self, angle):
        # given in degrees
        # save in radians
        # scale = min(max(angle / 6.0, 0.0), 1.0)
        self.angle = angle * math.pi / 180.0
        # self.sizeFadeWithDistance = scale
        self.reset()

    def set_size(self, width, height):
        self.cameraShape[0] = width
        self.cameraShape[1] = height
        self.reset()

    def update(self, debug_list=None):
        """
        Cameras operate in a lazy way: they don't actually update
        until needed because they are so expensive.
        """
        pass

    def _update(self):
        # Update timestamp:
        self.time = self.robot.world.time
        for i in range(self.cameraShape[0]):
            angle = i / self.cameraShape[0] * self.angle - self.angle / 2
            self.hits[i] = self.robot.cast_ray(
                self.robot.x,
                self.robot.y,
                math.pi / 2 - self.robot.direction - angle,
                1000,
            )

    def draw(self, backend):
        backend.set_fill(Color(0, 64, 0))
        backend.strokeStyle(None, 0)
        backend.draw_rect(5.0, -3.33, 1.33, 6.33)

    def find_closest_wall(self, hits):
        for hit in reversed(hits):  # reverse make it closest first
            if hit.height < 1.0:  # skip non-walls
                continue
            return hit.distance
        return float("inf")

    def take_picture(self, type="color"):
        try:
            from PIL import Image
        except ImportError:
            print("Pillow (PIL) module not available; take_picture() unavailable")
            return

        # Lazy; only get the data when we need it:
        self._update()
        pic = Image.new("RGBA", (self.cameraShape[0], self.cameraShape[1]))
        pic.__add__ = lambda other: print("other")
        pic_pixels = pic.load()
        # FIXME: probably should have a specific size rather than scale it to world
        size = max(self.robot.world.width, self.robot.world.height)
        hcolor = None
        # draw non-robot walls first:
        for i in range(self.cameraShape[0]):
            hits = [hit for hit in self.hits[i] if hit.height == 1.0]  # only walls
            if len(hits) == 0:
                continue
            hit = hits[-1]  # get closest
            high = None
            hcolor = None
            if hit:
                distance_ratio = max(min(1.0 - hit.distance / size, 1.0), 0.0)
                s = max(
                    min(1.0 - hit.distance / size * self.sizeFadeWithDistance, 1.0), 0.0
                )
                sc = max(
                    min(1.0 - hit.distance / size * self.colorsFadeWithDistance, 1.0),
                    0.0,
                )
                if type == "color":
                    r = hit.color.red * sc
                    g = hit.color.green * sc
                    b = hit.color.blue * sc
                elif type == "depth":
                    r = 255 * distance_ratio
                    g = 255 * distance_ratio
                    b = 255 * distance_ratio
                else:
                    avg = (hit.color.red + hit.color.green + hit.color.blue) / 3.0
                    r = avg * sc
                    g = avg * sc
                    b = avg * sc
                hcolor = Color(r, g, b)
                high = (1.0 - s) * self.cameraShape[1]
            else:
                high = 0

            horizon = self.cameraShape[1] / 2
            for j in range(self.cameraShape[1]):
                dist = max(min(abs(j - horizon) / horizon, 1.0), 0.0)
                if j < high / 2:  # sky
                    if type == "depth":
                        if self.reflectSky:
                            color = Color(255 * dist)
                        else:
                            color = Color(0)
                    elif type == "color":
                        color = Color(0, 0, 128)
                    else:
                        color = Color(128 / 3)
                    pic_pixels[i, j] = color.to_tuple()
                elif j < self.cameraShape[1] - high / 2:  # hit
                    if hcolor is not None:
                        pic_pixels[i, j] = hcolor.to_tuple()
                else:  # ground
                    if type == "depth":
                        if self.reflectGround:
                            color = Color(255 * dist)
                        else:
                            color = Color(0)
                    elif type == "color":
                        color = Color(0, 128, 0)
                    else:
                        color = Color(128 / 3)
                    pic_pixels[i, j] = color.to_tuple()

        # Other robots, draw on top of walls:
        self.obstacles = {}
        for i in range(self.cameraShape[0]):
            closest_wall_dist = self.find_closest_wall(self.hits[i])
            hits = [hit for hit in self.hits[i] if hit.height < 1.0]  # obstacles
            for hit in hits:
                if hit.distance > closest_wall_dist:
                    # Behind this wall
                    break
                distance_ratio = max(min(1.0 - hit.distance / size, 1.0), 0.0)
                s = max(
                    min(1.0 - hit.distance / size * self.sizeFadeWithDistance, 1.0), 0.0
                )
                sc = max(
                    min(1.0 - hit.distance / size * self.colorsFadeWithDistance, 1.0),
                    0.0,
                )
                distance_to = self.cameraShape[1] / 2 * (1.0 - sc)
                # scribbler was 30, so 0.23 height ratio
                # height is ratio, 0 to 1
                height = round(hit.height * self.cameraShape[1] / 2.0 * s)
                if type == "color":
                    r = hit.color.red * sc
                    g = hit.color.green * sc
                    b = hit.color.blue * sc
                elif type == "depth":
                    r = 255 * distance_ratio
                    g = 255 * distance_ratio
                    b = 255 * distance_ratio
                else:
                    avg = (hit.color.red + hit.color.green + hit.color.blue) / 3.0
                    r = avg * sc
                    g = avg * sc
                    b = avg * sc
                hcolor = Color(r, g, b)
                horizon = self.cameraShape[1] / 2
                self.record_obstacle(
                    hit.robot,
                    i,
                    self.cameraShape[1] - 1 - round(distance_to),
                    self.cameraShape[1] - height - 1 - 1 - round(distance_to),
                )
                if not hit.robot.has_image():
                    for j in range(height):
                        pic_pixels[
                            i, self.cameraShape[1] - j - 1 - round(distance_to)
                        ] = hcolor.to_tuple()
        self.show_obstacles(pic)
        return pic

    def show_obstacles(self, image):
        # FIXME: show back to front
        # FIXME: how to show when partially behind wall?
        for data in self.obstacles.values():
            if data["robot"].has_image():
                # the angle to me + offset for graphics + the robot angle:
                radians = (
                    math.atan2(
                        data["robot"].x - self.robot.x, data["robot"].y - self.robot.y
                    )
                    + math.pi / 2
                    + data["robot"].direction
                )
                degrees = round(radians * 180 / math.pi)
                picture = data["robot"].get_image(degrees)  # degrees
                x1, y1 = data["min_x"], data["min_y"]  # noqa: F841
                x2, y2 = data["max_x"], data["max_y"]
                try:  # like too small
                    picture.thumbnail((x2 - x1, 10000))  # to keep aspect ratio
                    # picture = picture.resize((x2 - x1, y2 - y1))
                    x3 = x2 - picture.height
                    y3 = y2 - picture.width
                    image.paste(picture, (x3, y3), picture)
                except Exception:
                    print("Exception in processing image")

    def record_obstacle(self, robot, x, y1, y2):
        if robot.name not in self.obstacles:
            self.obstacles[robot.name] = {
                "robot": robot,
                "max_x": float("-inf"),
                "max_y": float("-inf"),
                "min_x": float("inf"),
                "min_y": float("inf"),
            }
        self.obstacles[robot.name]["max_x"] = max(
            self.obstacles[robot.name]["max_x"], x
        )
        self.obstacles[robot.name]["min_x"] = min(
            self.obstacles[robot.name]["min_x"], x
        )
        self.obstacles[robot.name]["max_y"] = max(
            self.obstacles[robot.name]["max_y"], y1, y2
        )
        self.obstacles[robot.name]["min_y"] = min(
            self.obstacles[robot.name]["min_y"], y1, y2
        )

    def get_point_cloud(self):
        depth_pic = self.take_picture("depth")
        depth_pixels = depth_pic.load()
        color_pic = self.take_picture("color")
        color_pixels = color_pic.load()
        points = []
        for x in range(self.cameraShape[0]):
            for y in range(self.cameraShape[1]):
                dist_color = depth_pixels[x, y]
                color = color_pixels[x, y]
                if dist_color[0] != 255:
                    points.append(
                        [
                            self.cameraShape[0] - x - 1,
                            self.cameraShape[1] - y - 1,
                            dist_color[0],
                            color[0],
                            color[1],
                            color[2],
                        ]
                    )
        return points
