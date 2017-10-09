#!/usr/bin/env python3
import sge
import pygame.mixer
import os
import random
import glob
import json
import Core


def create_room(path, **kwargs):
    with open(path) as file:
        attributes = json.load(file)
        type_name = next(iter(attributes))
        args = attributes[type_name]
        return eval(type_name)(**kwargs, **args)


def randomize_layers(layers, sprites):
    for layer in layers:
        sprite = random.choice(sprites)
        layer.sprite = sprite


def align_layers(layers):
    for index, layer in enumerate(layers):
        layer.x = index * layer.sprite.width


class TitleScreen(sge.dsp.Room):

    def __init__(self, sprite_name, font=None, **kwargs):
        sprite = sge.gfx.Sprite(sprite_name, Core.IMG_PATH)
        layers = [sge.gfx.BackgroundLayer(sprite, 0, 0)]
        background = sge.gfx.Background(layers, sge.gfx.Color("white"))
        super().__init__(background=background, **kwargs)
        self.font = font


class PlayArea(sge.dsp.Room):

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        self._font = font

    def __init__(self, timer=60, font=None, layer_count=1, **kwargs):
        # Create backgrounds
        layers = [sge.gfx.BackgroundLayer(None, 0, 0) for count in range(layer_count)]
        background = sge.gfx.Background(layers, sge.gfx.Color("white"))
        super().__init__(background=background, **kwargs)
        self.timer = self.start_timer = timer
        self.sounds = {}
        self.font = font

    def event_room_start(self):
        self.sprite_timer = sge.gfx.Sprite(name="timerBG",
                                           directory="images")
        self.play_song(os.path.join(Core.SND_PATH, "Anxiety.ogg"))

        background_sprites = []
        for path in glob.iglob(os.path.join(Core.IMG_PATH, "wallPanel*.*")):
            filename = os.path.splitext(os.path.basename(path))[0]
            sprite = sge.gfx.Sprite(filename, directory=Core.IMG_PATH)
            background_sprites.append(sprite)
        randomize_layers(self.background.layers, background_sprites)
        align_layers(self.background.layers)

    def event_step(self, time_passed, delta_mult):
        sge.game.project_sprite(self.sprite_timer, 0, 0, 0)
        sge.game.project_text(self._font, str(int(self.timer)),
                              self.sprite_timer.width / 2,
                              self.sprite_timer.height / 2,
                              color=sge.gfx.Color("white"),
                              halign="left",
                              valign="middle")
        self.timer = Core.clamp(self.timer - time_passed / 1000,
                                0,
                                self.start_timer)

        if Core.Game.key_pressed("r"):
            self.reset()

    def play_sound(self, path):
        sound = None
        if path not in self.sounds:
            sound = pygame.mixer.Sound(path)
            self.sounds[path] = sound
        self.sounds[path].play()

    def play_song(self, path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(0)

    def reset(self):
        for obj in self.objects:
            reset = getattr(obj, "reset", None)
            if callable(reset):
                obj.reset()
        self.timer = self.start_timer
