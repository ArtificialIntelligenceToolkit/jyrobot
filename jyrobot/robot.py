import math

from .utils import (Color, Line, Point)
from .hit import Hit
from .sensors import Camera, DepthCamera, RangeSensor

class Robot():
    def __init__(self, config):
        self.initialize()
        self.name = config.get("name", "Robbie")
        self.x = config.get("x", 100)
        self.y = config.get("y", 100)
        self.direction = config.get("direction", 0) ## comes in as degrees
        self.direction = self.direction * math.pi / 180 ## save as radians
        color = config.get("color", None)
        if (color is not None):
            self.color = Color(color[0], color[1], color[2])
        else:
            self.color = Color(255, 0, 0)

        self.body = config.get("body", [])
        for cameraConfig in config.get("cameras", []):
            camera = None
            if (cameraConfig["type"] == "Camera"):
                camera = Camera(self, cameraConfig)
            elif (cameraConfig["type"] == "DepthCamera"):
                camera = DepthCamera(self, cameraConfig)
            else:
                print("Unknown camera type:", cameraConfig["type"])

            if (camera):
                self.cameras.append(camera)

        print("Done!")
        for rangeConfig in config.get("rangeSensors", []):
            sensor = RangeSensor(self, rangeConfig)
            self.range_sensors.append(sensor)

    def initialize(self):
        self.doTrace = True
        self.trace = []
        self.max_trace_length = 1000
        self.x = 0 ## cm
        self.y = 0 ## cm
        self.direction = 0 ## radians
        self.state = ""
        self.debug = False
        self.vx = 0.0 ## velocity in x direction, CM per second
        self.vy = 0.0 ## velocity in y direction, degrees per second
        self.va = 0.0 ## turn velocity
        self.stalled = False
        self.state = ""
        self.bounding_lines = [
            Line(Point(0,0), Point(0,0)),
            Line(Point(0,0), Point(0,0)),
            Line(Point(0,0), Point(0,0)),
            Line(Point(0,0), Point(0,0)),
        ]
        self.range_sensors = []
        self.cameras = []
        self.state = ""
        self.initBoundingBox()

    def setConfig(self, config):
        vx = config.get("vx", None)
        if (vx is not None):
            self.vx = vx

        vy = config.get("vy", None)
        if (vy is not None):
            self.vy = vy

        va = config.get("va", None)
        if (va is not None):
            self.va = va

    def forward(self, vx):
        self.vx = vx

    def backward(self, vx):
        self.vx = -vx

    def turn(self, va):
        self.va = va

    def stop(self):
        self.vx = 0.0
        self.vy = 0.0
        self.va = 0.0

    def ccw(self, ax, ay, bx, by,  cx, cy):
        ## counter clockwise
        return (((cy - ay) * (bx - ax)) > ((by - ay) * (cx - ax)))

    def intersect(self, ax, ay, bx, by, cx, cy, dx, dy):
        ## Return true if line segments AB and CD intersect
        return (self.ccw(ax, ay, cx, cy, dx, dy) != self.ccw(bx, by, cx, cy, dx, dy) and
                self.ccw(ax, ay, bx, by, cx, cy) != self.ccw(ax, ay, bx, by, dx, dy))

    def coefs(self, p1x, p1y, p2x, p2y):
        A = (p1y - p2y)
        B = (p2x - p1x)
        C = (p1x * p2y - p2x * p1y)
        return [
            A, B, -C
        ]

    def intersect_coefs(self, L1_0, L1_1, L1_2,
                    L2_0, L2_1, L2_2):
        D  = L1_0 * L2_1 - L1_1 * L2_0
        if (D != 0):
            Dx = L1_2 * L2_1 - L1_1 * L2_2
            Dy = L1_0 * L2_2 - L1_2 * L2_0
            x1 = Dx / D
            y1 = Dy / D
            return [
                x1, y1
            ]
        else:
            return None

    def intersect_hit(self, p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y):
        ## http:##stackoverflow.com/questions/20677795/find-the-point-of-intersecting-lines
        L1 = self.coefs(p1x, p1y, p2x, p2y)
        L2 = self.coefs(p3x, p3y, p4x, p4y)
        xy = self.intersect_coefs(L1[0], L1[1], L1[2],
                                  L2[0], L2[1], L2[2])
        ## now check to see on both segments:
        if (xy):
            lowx = min(p1x, p2x) - .1
            highx = max(p1x, p2x) + .1
            lowy = min(p1y, p2y) - .1
            highy = max(p1y, p2y) + .1
            if (lowx <= xy[0] and xy[0] <= highx and
                lowy <= xy[1] and xy[1] <= highy):
                lowx = min(p3x, p4x) - .1
                highx = max(p3x, p4x) + .1
                lowy = min(p3y, p4y) - .1
                highy = max(p3y, p4y) + .1
                if (lowx <= xy[0] and xy[0] <= highx and
                    lowy <= xy[1] and xy[1] <= highy):
                    return xy

        return None

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

    def castRay(self, x1, y1, a, maxRange, seeRobots):
        ## Just walls, not robots
        hits = []
        x2 = math.sin(a) * maxRange + x1
        y2 = math.cos(a) * maxRange + y1
        dist = None
        ##height

        for wall in self.world.walls:
            ## either seeRobots is true and not self, or only walls
            if ((seeRobots and (wall.robot is self)) or (not seeRobots and (wall.robot is not None))):
                continue
            for line in wall.lines:
                p1 = line.p1
                p2 = line.p2
                pos = self.intersect_hit(x1, y1, x2, y2, p1.x, p1.y, p2.x, p2.y)
                if (pos is not None):
                    dist = self.distance(pos[0], pos[1], x1, y1)
                    hits.append(Hit(1.0, pos[0], pos[1], dist, wall.color, x1, y1))

        if (len(hits) == 0):
            return None
        else:
            return self.min_hit(hits)

    def castRayRobot(self, x1, y1, a, maxRange):
        ## Just robots, not walls
        hits = []
        x2 = math.sin(a) * maxRange + x1
        y2 = math.cos(a) * maxRange + y1
        dist = None
        ##height

        for wall in self.world.walls:
            ## if a wall, or self, continue:
            if (wall.robot == None or wall.robot is self):
                continue
            for line in wall.lines:
                p1 = line.p1
                p2 = line.p2
                pos = self.intersect_hit(x1, y1, x2, y2,
                                                       p1.x, p1.y, p2.x, p2.y)
                if (pos is not None):
                    dist = self.distance(pos[0], pos[1], x1, y1)
                    hits.append(Hit(1.0, pos[0], pos[1], dist, wall.color, x1, y1))

        return hits

    def min_hit(self, hits):
        ## requires at least one Hit
        minimum = hits[0]
        for hit in hits:
            if (hit.distance < minimum.distance):
                minimum = hit

        return minimum

    def initBoundingBox(self):
        px = self.x
        py = self.y
        pdirection = self.direction
        p1 = self.rotateAround(px, py, 10, pdirection + math.pi/4 + 0 * math.pi/2)
        p2 = self.rotateAround(px, py, 10, pdirection + math.pi/4 + 1 * math.pi/2)
        p3 = self.rotateAround(px, py, 10, pdirection + math.pi/4 + 2 * math.pi/2)
        p4 = self.rotateAround(px, py, 10, pdirection + math.pi/4 + 3 * math.pi/2)
        self.updateBoundingBox(p1, p2, p3, p4)

    def updateBoundingBox(self, p1, p2,
                          p3, p4):
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

    def update(self, time_step):
        if (self.doTrace):
            self.trace.append(Point(self.x, self.y))
            if (len(self.trace) > self.max_trace_length):
                self.trace.shift()

        ##self.direction += PI/180
        tvx = self.vx * math.sin(-self.direction + math.pi/2) + self.vy * math.cos(-self.direction + math.pi/2) * time_step
        tvy = self.vx * math.cos(-self.direction + math.pi/2) - self.vy * math.sin(-self.direction + math.pi/2) * time_step
        ## proposed positions:
        px = self.x + tvx
        py = self.y + tvy
        pdirection = self.direction - self.va * time_step
        ## check to see if collision
        ## bounding box:
        p1 = self.rotateAround(px, py, 10, pdirection + math.pi/4 + 0 * math.pi/2)
        p2 = self.rotateAround(px, py, 10, pdirection + math.pi/4 + 1 * math.pi/2)
        p3 = self.rotateAround(px, py, 10, pdirection + math.pi/4 + 2 * math.pi/2)
        p4 = self.rotateAround(px, py, 10, pdirection + math.pi/4 + 3 * math.pi/2)

        self.updateBoundingBox(p1, p2, p3, p4)

        self.stalled = False
        ## if intersection, can't move:
        for wall in self.world.walls:
            if (wall.robot is self): ## if yourself, don't check for collision
                continue
            for line in wall.lines:
                w1 = line.p1
                w2 = line.p2
                if (self.intersect(p1[0], p1[1], p2[0], p2[1],
                                   w1.x, w1.y, w2.x, w2.y) or
                    self.intersect(p2[0], p2[1], p3[0], p3[1],
                                   w1.x, w1.y, w2.x, w2.y) or
                    self.intersect(p3[0], p3[1], p4[0], p4[1],
                                   w1.x, w1.y, w2.x, w2.y) or
                    self.intersect(p4[0], p4[1], p1[0], p1[1],
                                   w1.x, w1.y, w2.x, w2.y)):
                    self.stalled = True
                    break

        if (not self.stalled):
            ## if no intersection, make move
            self.x = px
            self.y = py
            self.direction = pdirection

        ## Range Sensors:
        for range_sensor in self.range_sensors:
            range_sensor.update(time_step)

        ## Cameras:
        for camera in self.cameras:
            camera.update(time_step)

    def rotateAround(self, x1, y1, length, angle):
        return [
            x1 + length * math.cos(-angle),
            y1 - length * math.sin(-angle)
        ]

    def draw(self, canvas):
        if (self.doTrace):
            canvas.strokeStyle(Color(200, 200, 200), 1)
            canvas.beginShape()
            for point in self.trace:
                canvas.vertex(point.x, point.y)

            canvas.stroke()

        if (self.debug):
            canvas.strokeStyle(Color(255), 1)
            canvas.line(self.bounding_lines[0].p1.x, self.bounding_lines[0].p1.y,
                        self.bounding_lines[0].p2.x, self.bounding_lines[0].p2.y)

            canvas.line(self.bounding_lines[1].p1.x, self.bounding_lines[1].p1.y,
                        self.bounding_lines[1].p2.x, self.bounding_lines[1].p2.y)

            canvas.line(self.bounding_lines[2].p1.x, self.bounding_lines[2].p1.y,
                        self.bounding_lines[2].p2.x, self.bounding_lines[2].p2.y)

            canvas.line(self.bounding_lines[3].p1.x, self.bounding_lines[3].p1.y,
                        self.bounding_lines[3].p2.x, self.bounding_lines[3].p2.y)

        canvas.pushMatrix()
        canvas.translate(self.x, self.y)
        canvas.rotate(self.direction)

        ## body:
        if (self.stalled):
            canvas.fill(Color(128, 128, 128))
            canvas.strokeStyle(Color(255), 1)
        else:
            canvas.fill(self.color)
            canvas.noStroke()

        canvas.beginShape()
        for i in range(len(self.body)):
            canvas.vertex(self.body[i][0], self.body[i][1])

        canvas.endShape()
        canvas.noStroke()
        ## Draw wheels:
        canvas.fill(Color(0))
        canvas.rect(-3.33, -7.67, 6.33, 1.67)
        canvas.rect(-3.33, 6.0, 6.33, 1.67)
        ## hole:
        canvas.fill(Color(0, 64, 0))
        canvas.strokeStyle(None, 0)
        canvas.ellipse(0, 0, 1.67, 1.67)

        for camera in self.cameras:
            camera.draw(canvas)

        canvas.popMatrix()

        for range_sensor in self.range_sensors:
            range_sensor.draw(canvas)
