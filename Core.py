#!/usr/bin/env python3
import sge
import json


# Constants
IMG_PATH = "images"
SND_PATH = "sounds"


def clamp(number, low, high):
    return max(low, min(high, number))


class Game(sge.dsp.Game):

    keys = {}
    sprites = {}

    @staticmethod
    def key_pressed(key):
        if key not in Game.keys:
            Game.keys[key] = False
        return Game.keys[key]

    @staticmethod
    def consume_key(key):
        Game.keys[key] = False

    @classmethod
    def config_create(cls, path):
        with open(path) as file:
            attributes = json.load(file)
            return cls(**attributes)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rooms = []
        self.iter_room = iter(self.rooms)
        self.view = sge.dsp.View(0, 0, width=self.width, height=self.height)

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

    def get_room(self, index):
        rooms = self.rooms[index:]
        self.iter_room = iter(rooms)
        return next(self.iter_room, None)

    def next_room(self):
        return next(self.iter_room, None)
