#!/usr/bin/env python3
import sge
import random


def clamp(number, low, high):
    return max(low, min(high, number))


def randomize_layers(layers, sprites):
    for layer in layers:
        sprite = random.choice(sprites)
        layer.sprite = sprite


class Game(sge.dsp.Game):

    @staticmethod
    def key_pressed(key):
        if key not in Game.keys:
            Game.keys[key] = False
        return Game.keys[key]

    @staticmethod
    def consume_key(key):
        Game.keys[key] = False

    def __init__(self, width=640, height=480, fullscreen=False, scale=None,
                 scale_proportional=True, scale_method=None, fps=60,
                 delta=False, delta_min=15, delta_max=None, grab_input=False,
                 window_text=None, window_icon=None,
                 collision_events_enabled=True):
        super().__init__(width, height, fullscreen, scale,
                         scale_proportional, scale_method, fps,
                         delta, delta_min, delta_max, grab_input,
                         window_text, window_icon,
                         collision_events_enabled)
        Game.keys = {}

    def event_step_late(self, time_passed, delta_mult):
        for key, value in Game.keys.items():
            Game.keys[key] = False
        pass

    def event_key_press(self, key, char):
        Game.keys[key] = True
        if key == 'escape':
            self.event_close()

    def event_key_release(self, key):
        Game.keys[key] = False

    def event_close(self):
        self.end()


class Room(sge.dsp.Room):

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        self._font = font

    def __init__(self, objects=(), width=None, height=None, views=None,
                 background=None, background_x=0, background_y=0,
                 object_area_width=None, object_area_height=None, timer=60):
        super().__init__(objects, width, height, views,
                         background, background_x, background_y,
                         object_area_width, object_area_height)
        self.timer = timer * 1000
        pass

    def event_room_start(self):
        self.sprite_timer = sge.gfx.Sprite(name="timerBG",
                                           directory="images")

    def event_step(self, time_passed, delta_mult):
        sge.game.project_sprite(self.sprite_timer, 0, 0, 0)
        sge.game.project_text(self._font, str(self.timer / 1000),
                              self.sprite_timer.width / 2,
                              self.sprite_timer.height / 2,
                              color=sge.gfx.Color("white"), halign="left",
                              valign="middle")
        self.timer -= time_passed
        pass
