import sge
import pygame.mixer
import os
import json
import Core


def build_room(path, **kwargs):
    with open(path) as file:
        attributes = json.load(file)
        type_name = next(iter(attributes))
        args = attributes[type_name]
        return eval(type_name)(**kwargs, **args)


class TitleScreen(sge.dsp.Room):
    pass


class PlayArea(sge.dsp.Room):

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        self._font = font

    def __init__(self, timer=60, font=None, **kwargs):
        super().__init__(**kwargs)
        self.timer = self.start_timer = timer
        self.sounds = {}
        self.font = font

    def event_room_start(self):
        self.sprite_timer = sge.gfx.Sprite(name="timerBG",
                                           directory="images")
        self.play_song(os.path.join(Core.SND_PATH, "Anxiety.ogg"))
        # TODO create objects from json file

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
            sound = self.sounds[path] = pygame.mixer.Sound(path)
        sound.play()

    def play_song(self, path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(0)

    def reset(self):
        for obj in self.objects:
            reset = getattr(obj, "reset", None)
            if callable(reset):
                obj.reset()
        self.timer = self.start_timer
