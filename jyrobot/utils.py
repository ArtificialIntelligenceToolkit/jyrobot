
class Canvas():
    def __init__(self, canvas, width, height, scale):
        self._scale = scale
        self.width = width
        self.height = height
        self.canvas = canvas ## document.createElement('canvas')
        self.canvas.width = self.width
        self.canvas.height = self.height
        ## self.canvas.style.zIndex   = "8"
        ## self.canvas.style.position = "absolute"
        ## self.canvas.style.border   = "1px solid"
        self.canvasGC = None ## self.canvas.getContext('2d')! FIXME
        self.gc = None ## FIXME
        self.shape = false ##  in the middle of a shape?
        self.scale(self._scale, self._scale)

    def clear(self):
        self.gc.clearRect(0, 0, self.width, self.height)

    def font(selfstyle):
        self.gc.font = style

    def text(self, t, x, y):
        self.gc.fillText(t, x, y)

    def lineWidth(self, width):
        self.gc.lineWidth = width

    def strokeStyle(self, color, width):
        if (color):
            self.gc.strokeStyle = str(color)
        else:
            self.gc.strokeStyle = ""
        self.gc.lineWidth = width

    def stroke(self):
        self.gc.stroke()

    def noStroke(self):
        self.gc.strokeStyle = ""

    def fill(self, color):
        if (color):
            self.gc.fillStyle = str(color)
        else:
            self.gc.fillStyle = ""

    def noFill(self):
        self.gc.fillStyle = ""

    def line(self, x1, y1, x2, y2):
        self.beginShape()
        self.gc.moveTo(x1, y1)
        self.gc.lineTo(x2, y2)
        self.gc.stroke()

    def pushMatrix(self):
        self.gc.save()

    def popMatrix(self):
        self.gc.restore()

    def translate(selfx, y):
        self.gc.translate(x, y)

    def scale(self, x, y):
        self.gc.scale(x, y)

    def resetScale(self):
        self.gc.setTransform(1, 0, 0, 1, 0, 0)

    def rotate(self, angle):
        self.gc.rotate(angle)

    def beginShape(self):
        self.shape = false
        return self.gc.beginPath()

    def endShape(self):
        self.gc.closePath()
        self.gc.fill()

    def vertex(self, x, y):
        if (self.shape):
            self.gc.lineTo(x, y)
        else:
            self.gc.moveTo(x, y)
            self.shape = true

    def rect(self, x, y, width, height):
        self.gc.fillRect(x, y, width, height)

    def ellipse(self, x, y, radiusX, radiusY):
        self.gc.beginPath()
        self.gc.ellipse(x, y, radiusX, radiusY, 0, 0, Math.PI * 2)
        self.gc.fill()

    def picture(self, pic, x, y, scale=1.0):
        scaled = self.scaleImageData(pic.getData(), scale)
        self.gc.putImageData(scaled, x, y)

    def scaleImageData(self, imageData, scale):
        scaled = self.gc.createImageData(imageData.width * scale, imageData.height * scale)
        subLine = self.gc.createImageData(scale, 1).data
        for row in range(imageData.height):
            for col in range(imageData.width):
                sourcePixel = imageData.data.subarray(
                    (row * imageData.width + col) * 4,
                    (row * imageData.width + col) * 4 + 4
                )
                for x in range(scale):
                    subLine.set(sourcePixel, x*4)
                for y in range(scale):
                    destRow = row * scale + y
                    destCol = col * scale
                    scaled.data.set(subLine, (destRow * scaled.width + destCol) * 4)

        return scaled

    def arc(self, x, y, width, height, startAngle, endAngle):
        ##  Draw the pie:
        self.gc.strokeStyle = ""
        self.gc.beginPath()
        self.gc.moveTo(x, y)
        self.gc.arc(x, y, width, startAngle, endAngle)
        self.gc.lineTo(x, y)
        self.gc.fill()

        ##  Draw the arc:
        self.gc.strokeStyle = ""
        self.gc.beginPath()
        self.gc.arc(x, y, width, startAngle, endAngle)
        self.gc.stroke()

class Matrix():
    def __init__(self, rows, cols, value = 0):
        super(rows)
        for i in range(rows):
            this[i] = Array(cols)
            for j in range(cols):
                this[i][j] = value

class Color():
    def __init__(self, red, green=None, blue=None, alpha=None):
        self.red = red
        if (green != None):
            self.green = green
        else:
            self.green = red
        if (blue != None):
            self.blue = blue
        else:
            self.blue = red
        if (alpha != None):
            self.alpha = alpha
        else:
            self.alpha = 255

    def toHex(self, c):
        #hex = c.toString(16)
        #return hex.length == 1 ? "0" + hex : hex
        pass # FIXME

    def toString(self):
        return ("#" + self.toHex(self.red) + self.toHex(self.green) +
                self.toHex(self.blue) + self.toHex(self.alpha))

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

class Picture():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.imageData = None ## new ImageData(self.width, self.height) FIXME

    def position(self, x, y):
        return (y * self.width * 4) + (x * 4)

    def set(self, x, y, color):
        pos = self.position(x, y)
        self.imageData.data[pos + 0] = color.red
        self.imageData.data[pos + 1] = color.green
        self.imageData.data[pos + 2] = color.blue
        self.imageData.data[pos + 3] = color.alpha

    def get(self, x, y):
        return self.imageData.data[(x + y * self.width) * 4]

    def getData(self):
        return self.imageData
