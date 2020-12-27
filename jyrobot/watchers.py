from ipylab import JupyterFrontEnd, Panel
from bqplot import (
    LinearScale, Bars, Lines, Axis, Figure
)

class Watcher:
    def __init__(self, robot, x_str, y_str):
        self.robot = robot
        self.x_str = x_str
        self.y_str = y_str
        self.x_values = []
        self.y_values = []

        x_sc = LinearScale()
        y_sc = LinearScale()

        line = Lines(x=[], y=[], scales={'x': x_sc, 'y': y_sc},
                     stroke_width=3, colors=['red'])

        ax_x = Axis(scale=x_sc, label=x_str)
        ax_y = Axis(scale=y_sc, orientation='vertical', label=y_str)

        self.widget = Figure(marks=[line], axes=[ax_x, ax_y], title="%s vs. %s" % (x_str, y_str))

    def draw(self):
        import numpy as np

        with self.widget.marks[0].hold_sync():
            self.widget.marks[0].x = np.array(self.x_values)
            self.widget.marks[0].y = np.array(self.y_values)

    def update(self):
        if self.x_str.startswith("["):
            self.x_values.append(eval("self.robot" + self.x_str))
        else:
            self.x_values.append(eval("self.robot." + self.x_str))

        if self.y_str.startswith("["):
            self.y_values.append(eval("self.robot" + self.y_str))
        else:
            self.y_values.append(eval("self.robot." + self.y_str))

    def reset(self):
        self.x_values = []
        self.y_values = []
