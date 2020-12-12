import math

from .utils import (Color, Picture)

def arange(start, stop, step):
    current = start
    while current <= stop:
        yield current
        current += step

class RangeSensor():
    """
       A range sensor that reads "reading" when
       no obstacle has been detected. "reading" is
       a ratio of distance/max, and "distance" is
       the reading in CM.
    """

    def __init__(self, robot, config):
        self.time = 0
        self.reading = 1.0
        self.robot = robot
        self.position = config.get("position", 10)
        self.direction = config.get("direction", 0) ## comes in degrees
        self.direction = self.direction * math.pi * 180 ## save as radians
        self.max = config.get("max", 100)
        self.width = config.get("width", 1.0)
        self.distance = self.reading * self.max

    def update(self, time):
        p = self.robot.rotateAround(
            self.robot.x, self.robot.y, self.position, self.robot.direction + self.direction)
        self.setReading(1.0)
        if (self.width != 0):
            for incr in arange(-self.width/2, self.width/2, self.width/2):
                hit = self.robot.castRay(
                    p[0], p[1], -self.robot.direction + math.pi/2.0  + incr,
                    self.max, True)
                if (hit):
                    if (hit.distance < self.getDistance()):
                        self.setDistance(hit.distance)
        else:
            hit = self.robot.castRay(
                p[0], p[1], -self.robot.direction + math.pi/2.0,
                self.max, True)
            if (hit):
                if (hit.distance < self.getDistance()):
                    self.setDistance(hit.distance)

    def draw(self, canvas):
        if (self.getReading() < 1.0):
            canvas.strokeStyle(Color(255), 1)
        else:
            canvas.strokeStyle(Color(0), 1)

        canvas.fill(Color(128, 0, 128, 64))
        p1 = self.robot.rotateAround(self.robot.x, self.robot.y, self.position, self.robot.direction + self.direction)
        dist = self.getDistance()
        if (self.width > 0):
            canvas.arc(p1[0], p1[1], dist, dist,
                       self.robot.direction - self.width/2,
                       self.robot.direction + self.width/2)
        else:
            end = self.robot.rotateAround(p1[0], p1[1], dist, self.direction + self.direction)
            canvas.line(p1[0], p1[1], end[0], end[1])

    def getDistance(self):
        return self.distance

    def getReading(self):
        return self.reading

    def setDistance(self, distance):
        self.distance = distance
        self.reading = distance/self.max

    def setReading(self, reading):
        self.reading = reading
        self.distance = reading * self.max

class Camera():
    def __init__(self, robot, config):
        self.robot = robot
        self.cameraShape = [config.get("width", 256), config.get("height", 128)]
        ## 0 = no fade, 1.0 = max fade
        self.colorsFadeWithDistance = config.get("colorsFadeWithDistance", 1.0)
        self.angle = config.get("angle", 60) ## comes in degrees
        self.angle = self.angle * math.pi / 180 ## save in radians
        self.camera = [0 for i in range(self.cameraShape[0])]
        self.robotHits = [None for i in range(self.cameraShape[0])]

    def update(self, time):
        for i in range(self.cameraShape[0]):
            angle = i/self.cameraShape[0] * self.angle - self.angle/2
            self.camera[i] = self.robot.castRay(
                self.robot.x, self.robot.y,
                math.pi/2 -self.robot.direction - angle, 1000, False)

        ## Only needed if other robots:
        for i in range(self.cameraShape[0]):
            angle = i/self.cameraShape[0] * self.angle - self.angle/2
            self.robotHits[i] = self.robot.castRayRobot(
                self.robot.x, self.robot.y,
                math.pi/2 -self.robot.direction - angle, 1000)

    def draw(self, canvas):
        canvas.fill(Color(0, 64, 0))
        canvas.strokeStyle(None, 0)
        canvas.rect(5.0, -3.33, 1.33, 6.33)

    def takePicture(self):
        pic = Picture(self.cameraShape[0], self.cameraShape[1])
        size = max(self.robot.world.w, self.robot.world.h)
        hcolor = None
        ## draw non-robot walls first:
        for i in range(self.cameraShape[0]):
            hit = self.camera[i]
            high = None
            hcolor = None
            if (hit):
                s = max(min(1.0 - hit.distance/size, 1.0), 0.0)
                sc = max(min(1.0 - hit.distance/size * self.colorsFadeWithDistance, 1.0), 0.0)
                r = hit.color.red
                g = hit.color.green
                b = hit.color.blue
                hcolor = Color(r * sc, g * sc, b * sc)
                high = (1.0 - s) * self.cameraShape[1]
            else:
                high = 0

            for j in range(self.cameraShape[1]):
                if (j < high/2): ## sky
                    pic.set(i, j, Color(0, 0, 128))
                elif (j < self.cameraShape[1] - high/2): ## hit
                    if (hcolor is not None):
                        pic.set(i, j, hcolor)
                else: ## ground
                    pic.set(i, j, Color(0, 128, 0))

        ## Other robots, draw on top of walls:
        for i in range(self.cameraShape[0]):
            hits = self.robotHits[i]
            hits.sort(key=lambda a: a.distance) ## further away first
            for hit in hits:
                if (self.camera[i] and (hit.distance > self.camera[i].distance)):
                    ## Behind this wall
                    break
                s = max(min(1.0 - hit.distance/size, 1.0), 0.0)
                sc = max(min(1.0 - hit.distance/size * self.colorsFadeWithDistance, 1.0), 0.0)
                distance_to = self.cameraShape[1]/2 * (1.0 - s)
                height = round(30 * s)
                r = hit.color.red
                g = hit.color.green
                b = hit.color.blue
                hcolor = Color(r * sc, g * sc, b * sc)
                for j in range(height):
                    pic.set(i, self.cameraShape[1] - j - 1 - round(distance_to), hcolor)

        return pic


class DepthCamera(Camera):
    def __init__(self, robot, config):
        super().__init__(robot, config)
        self.reflectGround = config.get("reflectGround", True)
        self.reflectSky = config.get("reflectGround", False)

    def takePicture(self):
        pic = Picture(self.cameraShape[0], self.cameraShape[1])
        size = max(self.robot.world.w, self.robot.world.h)
        hcolor = None
        ## draw non-robot walls first:
        for i in range(self.cameraShape[0]):
            hit = self.camera[i]
            high = None
            hcolor = None
            if (hit):
                s = max(min(1.0 - hit.distance/size, 1.0), 0.0)
                sc = max(min(1.0 - hit.distance/size * self.colorsFadeWithDistance, 1.0), 0.0)
                hcolor = Color(255 * sc)
                high = (1.0 - s) * self.cameraShape[1]
            else:
                high = 0

            horizon = self.cameraShape[1]/2
            for j in range(self.cameraShape[1]):
                sky = max(min(1.0 - j/horizon * self.colorsFadeWithDistance, 1.0), 0.0)
                ground = max(min((j - horizon)/horizon * self.colorsFadeWithDistance, 1.0), 0.0)
                if (j < high/2): ## sky
                    if (self.reflectSky):
                        color = Color(255 - (255 * sky))
                        pic.set(i, j, color)

                elif (j < self.cameraShape[1] - high/2): ## hit
                    if (hcolor is not None):
                        pic.set(i, j, hcolor)
                else: ## ground
                    if (self.reflectGround):
                        color = Color(255 * ground)
                        pic.set(i, j, color)

        ## Other robots, draw on top of walls:
        for i in range(self.cameraShape[0]):
            hits = self.robotHits[i]
            hits.sort(key=lambda a: a.distance) ## further away first
            for hit in hits:
                if (self.camera[i] and (hit.distance > self.camera[i].distance)):
                    ## Behind this wall
                    break
                s = max(min(1.0 - hit.distance/size, 1.0), 0.0)
                sc = max(min(1.0 - hit.distance/size * self.colorsFadeWithDistance, 1.0), 0.0)
                distance_to = self.cameraShape[1]/2 * (1.0 - s)
                height = round(30 * s)
                hcolor = Color(255 * sc)
                for j in range(height):
                    pic.set(i, self.cameraShape[1] - j - 1 - round(distance_to), hcolor)

        return pic
