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

from IPython.display import display
from ipywidgets import Button, FloatSlider, FloatText, HBox, Label, Layout, Output, VBox

from .world import World


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
        self.poses = []
        self.world = world
        # Copy of the world for creating playback:
        self.world_copy = World(**world.to_json())
        self.widget = Player("Time:", self.goto, 0, play_rate)

    def draw(self):
        self.widget.update_length(len(self.poses))

    def update(self):
        # Record the poses from the real world:
        poses = []
        for robot in self.world:
            poses.append((robot.x, robot.y, robot.direction))
        self.poses.append(poses)

    def reset(self):
        self.poses = []

    def goto(self, time):
        index = round(time / 0.1)
        # place robots where they go in copy:
        if index < len(self.poses):
            for i, pose in enumerate(self.poses[index]):
                x, y, a = pose
                self.world_copy[i]._set_pose(x, y, a)
        self.world_copy.time = time
        self.world_copy.update()
        # FIXME: show trace correctly in copy
        picture = self.world_copy.take_picture()
        return picture


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
        self.control_slider.max = round(max(self.length * 0.1 - 0.1, 0), 1)

    def goto(self, position):
        #### Position it:
        if position == "begin":
            self.control_slider.value = 0.0
        elif position == "end":
            self.control_slider.value = round(self.length * 0.1 - 0.1, 1)
        elif position == "prev":
            if self.control_slider.value - 0.1 < 0:
                self.control_slider.value = round(
                    self.length * 0.1 - 0.1, 1
                )  # wrap around
            else:
                self.control_slider.value = round(
                    max(self.control_slider.value - 0.1, 0), 1
                )
        elif position == "next":
            if round(self.control_slider.value + 0.1, 1) > round(
                self.length * 0.1 - 0.1, 1
            ):
                self.control_slider.value = 0  # wrap around
            else:
                self.control_slider.value = round(
                    min(self.control_slider.value + 0.1, self.length * 0.1 - 0.1), 1
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
            max=max(round(self.length * 0.1 - 0.1, 1), 0.0),
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
