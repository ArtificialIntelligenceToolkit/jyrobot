# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from ipycanvas import hold_canvas

from .robot import Robot
from .utils import Color, Line, Point


class Wall:
    def __init__(self, color, robot, *lines):
        self.color = color
        self.lines = lines
        self.robot = robot


class World:
    def __init__(self, config, canvas=None):
        self.config = config
        self.canvas = canvas
        self.reset()
        if canvas:
            self.update()
            self.draw()

    def reset(self):
        self.time_step = 0.10
        self.time = 0.0
        self.at_x = 0
        self.at_y = 0
        self.robots = []
        self.walls = []
        self.boundary_wall_width = 1
        self.time = 0
        self.setConfig(self.config.get("world", {}))
        self.boundary_wall_color = Color(128, 0, 128)
        self.ground_color = Color(0, 128, 0)
        ## Put a wall around boundary:
        p1 = Point(0, 0)
        p2 = Point(0, self.h)
        p3 = Point(self.w, self.h)
        p4 = Point(self.w, 0)
        ## Not a box, but surround area with four walls:
        self.addWall(self.boundary_wall_color, None, Line(p1, p2))
        self.addWall(self.boundary_wall_color, None, Line(p2, p3))
        self.addWall(self.boundary_wall_color, None, Line(p3, p4))
        self.addWall(self.boundary_wall_color, None, Line(p4, p1))
        ## Create robot, and add to world:
        for robotConfig in self.config.get("robots", []):
            robot = Robot(robotConfig)
            self.addRobot(robot)

    def setConfig(self, config):
        self.w = config.get("width", 500)
        self.h = config.get("height", 250)
        for box in config.get("boxes", []):
            self.addBox(
                Color(box["color"][0], box["color"][1], box["color"][2]),
                box["p1"]["x"],
                box["p1"]["y"],
                box["p2"]["x"],
                box["p2"]["y"],
            )

    def format(self, v):
        return v  # parseFloat(v.toFixed(2))

    def addBox(self, color, x1, y1, x2, y2):
        p1 = Point(x1, y1)
        p2 = Point(x2, y1)
        p3 = Point(x2, y2)
        p4 = Point(x1, y2)
        ## Pairs of points make Line:
        self.addWall(
            color, None, Line(p1, p2), Line(p2, p3), Line(p3, p4), Line(p4, p1)
        )

    def addWall(self, c, robot=None, *lines):
        self.walls.append(Wall(c, robot, *lines))

    def addRobot(self, robot):
        self.robots.append(robot)
        robot.world = self
        self.addWall(robot.color, robot, *robot.bounding_lines)

    def seconds(self, seconds=5.0, function=None, time_step=None, show=True):
        time_step = time_step if time_step is not None else self.time_step
        count = round(seconds / time_step)
        self.steps(count, function, time_step, show)

    def steps(self, steps=1, function=None, time_step=None, show=True):
        time_step = time_step if time_step is not None else self.time_step
        for step in range(steps):
            self.step(time_step, show=show)
            if function is not None:
                stop = function(self)
                if stop:
                    break

    def step(self, time_step=None, show=True):
        time_step = time_step if time_step is not None else self.time_step
        for robot in self.robots:
            robot.step(time_step)
        self.time += time_step
        self.update(show)

    def update(self, show=True):
        ## Update robots:
        for robot in self.robots:
            robot.update()
        if show and self.canvas:
            self.draw()

    def draw(self, canvas=None):
        canvas = canvas if canvas is not None else self.canvas
        with hold_canvas(canvas.gc):
            canvas.clear()
            canvas.noStroke()
            canvas.fill(self.ground_color)
            canvas.rect(self.at_x, self.at_y, self.w, self.h)
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
            for robot in self.robots:
                robot.draw(canvas)
