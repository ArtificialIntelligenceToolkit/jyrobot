# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import threading
import time
import logging

from IPython.display import display
from ipywidgets import Button, FloatSlider, FloatText, HBox, Label, Layout, Output, VBox, Image

from .utils import Point, image_to_png
from .world import World


class RobotWatcher:
    def __init__(self, robot, size=100):
        self.robot = robot
        self.size = size
        self.widget = Image()
        self.draw()

    def draw(self):
        if self.robot.world is None:
            print("This robot is not in a world")
            return

        picture = self.robot.world.take_picture()
        start_x = round(max(self.robot.x * self.robot.world.scale - self.size / 2, 0))
        start_y = round(max(self.robot.y * self.robot.world.scale - self.size / 2, 0))
        rectangle = (
            start_x,
            start_y,
            min(start_x + self.size, self.robot.world.width * self.robot.world.scale),
            min(start_y + self.size, self.robot.world.height * self.robot.world.scale),
        )
        picture = picture.crop(rectangle)
        self.widget.value = image_to_png(picture)

    def update(self):
        pass

    def reset():
        pass


class CameraWatcher:
    def __init__(self, camera):
        self.camera = camera
        self.widget = Image()
        self.draw()

    def draw(self):
        picture = self.camera.take_picture()
        self.widget.value = image_to_png(picture)

    def update(self):
        pass

    def reset():
        pass


class _Player(threading.Thread):
    """
    Background thread for running a player.
    """

    def __init__(self, controller, time_wait=0.5):
        self.controller = controller
        threading.Thread.__init__(self)
        self.time_wait = time_wait
        self.can_run = threading.Event()
        self.can_run.clear()  # paused
        self.daemon = True  # allows program to exit without waiting for join

    def run(self):
        while True:
            self.can_run.wait()
            self.controller.goto("next")
            time.sleep(self.time_wait)

    def pause(self):
        self.can_run.clear()

    def resume(self):
        self.can_run.set()


class Recorder:
    def __init__(self, world, play_rate=0.1):
        self.states = []
        self.orig_world = world
        # Copy of the world for creating playback:
        self.world = World(**world.to_json())
        self.widget = Player("Time:", self.goto, 0, play_rate)

    def draw(self):
        self.widget.update_length(len(self.states))

    def update(self):
        # Record the states from the real world:
        states = []
        for robot in self.orig_world:
            states.append((robot.x, robot.y, robot.direction, robot.vx, robot.vy, robot.va, robot.stalled))
        self.states.append(states)

    def reset(self):
        self.states = []

    def get_trace(self, robot_index, current_index, max_length):
        # return as [Point(x,y), direction]
        start_index = max(current_index - max_length, 0)
        return [
            (Point(x, y), a)
            for (x, y, a, vx, vy, va, stalled) in [state[robot_index] for state in self.states[start_index : current_index + 1]]
        ]

    def goto(self, time):
        index = round(time / 0.1)
        # place robots where they go in copy:
        if len(self.states) == 0:
            for i, orig_robot in enumerate(self.orig_world):
                x, y, a, vx, vy, va, stalled = orig_robot.x, orig_robot.y, orig_robot.direction, orig_robot.vx, orig_robot.vy, orig_robot.va, orig_robot.stalled
                self.world[i]._set_pose(x, y, a)
                self.world[i].vx = vx
                self.world[i].vy = vy
                self.world[i].va = va
                self.world[i].stalled = stalled
                self.world[i].trace[:] = []
        else:
            index = max(min(len(self.states) - 1, index), 0)
            for i, state in enumerate(self.states[index]):
                x, y, a, vx, vy, va, stalled = state
                self.world[i]._set_pose(x, y, a)
                self.world[i].vx = vx
                self.world[i].vy = vy
                self.world[i].va = va
                self.world[i].stalled = stalled
                if self.world[i].do_trace:
                    self.world[i].trace = self.get_trace(i, index, self.world[i].max_trace_length)
        self.world.time = time
        self.world.update()
        picture = self.world.take_picture()
        return picture

    def watch(self, play_rate=None):
        if play_rate is not None:
            self.widget.player.time_wait = play_rate
        return self.widget


class Player(VBox):
    def __init__(self, title, function, length, play_rate=0.1):
        """
        function - takes a slider value and returns displayables
        """
        self.player = _Player(self, play_rate)
        self.player.start()
        self.title = title
        self.function = function
        self.length = length
        self.output = Output()
        self.position_text = FloatText(value=0.0, layout=Layout(width="100%"))
        self.total_text = Label(
            value="of %s" % round(self.length * 0.1, 1), layout=Layout(width="100px")
        )
        controls = self.make_controls()
        super().__init__([controls, self.output])

    def update_length(self, length):
        self.length = length
        self.total_text.value = "of %s" % round(self.length * 0.1, 1)
        self.control_slider.max = round(max(self.length * 0.1, 0), 1)

    def goto(self, position):
        #### Position it:
        if position == "begin":
            self.control_slider.value = 0.0
        elif position == "end":
            self.control_slider.value = round(self.length * 0.1, 1)
        elif position == "prev":
            if self.control_slider.value - 0.1 < 0:
                self.control_slider.value = round(self.length * 0.1, 1)  # wrap around
            else:
                self.control_slider.value = round(
                    max(self.control_slider.value - 0.1, 0), 1
                )
        elif position == "next":
            if round(self.control_slider.value + 0.1, 1) > round(self.length * 0.1, 1):
                self.control_slider.value = 0  # wrap around
            else:
                self.control_slider.value = round(
                    min(self.control_slider.value + 0.1, self.length * 0.1), 1
                )
        self.position_text.value = round(self.control_slider.value, 1)

    def toggle_play(self, button):
        ## toggle
        if self.button_play.description == "Play":
            self.button_play.description = "Stop"
            self.button_play.icon = "pause"
            self.player.resume()
        else:
            self.button_play.description = "Play"
            self.button_play.icon = "play"
            self.player.pause()

    def make_controls(self):
        button_begin = Button(icon="fast-backward", layout=Layout(width="100%"))
        button_prev = Button(icon="backward", layout=Layout(width="100%"))
        button_next = Button(icon="forward", layout=Layout(width="100%"))
        button_end = Button(icon="fast-forward", layout=Layout(width="100%"))
        self.button_play = Button(
            icon="play", description="Play", layout=Layout(width="100%")
        )
        self.control_buttons = HBox(
            [
                button_begin,
                button_prev,
                self.position_text,
                button_next,
                button_end,
                self.button_play,
            ],
            layout=Layout(width="100%", height="50px"),
        )
        self.control_slider = FloatSlider(
            description=self.title,
            continuous_update=False,
            min=0.0,
            step=0.1,
            max=max(round(self.length * 0.1, 1), 0.0),
            value=0.0,
            readout_format=".1f",
            style={"description_width": "initial"},
            layout=Layout(width="100%"),
        )
        ## Hook them up:
        button_begin.on_click(lambda button: self.goto("begin"))
        button_end.on_click(lambda button: self.goto("end"))
        button_next.on_click(lambda button: self.goto("next"))
        button_prev.on_click(lambda button: self.goto("prev"))
        self.button_play.on_click(self.toggle_play)
        self.control_slider.observe(self.update_slider_control, names="value")
        controls = VBox(
            [
                HBox(
                    [self.control_slider, self.total_text], layout=Layout(height="40px")
                ),
                self.control_buttons,
            ],
            layout=Layout(width="100%"),
        )
        controls.on_displayed(lambda widget: self.initialize())
        return controls

    def initialize(self):
        """
        Setup the displayer ids to map results to the areas.
        """
        results = self.function(self.control_slider.value)
        if not isinstance(results, (list, tuple)):
            results = [results]
        self.displayers = [display(x, display_id=True) for x in results]

    def update_slider_control(self, change):
        """
        If the slider changes the value, call the function
        and update display areas.
        """
        if change["name"] == "value":
            self.position_text.value = self.control_slider.value
            self.output.clear_output(wait=True)
            results = self.function(self.control_slider.value)
            if not isinstance(results, (list, tuple)):
                results = [results]
            for i in range(len(self.displayers)):
                self.displayers[i].update(results[i])
