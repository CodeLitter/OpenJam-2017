#!/usr/bin/env python3
import sge


class Game(sge.dsp.Game):

    def event_key_press(self, key, char):
        if key == 'escape':
            self.event_close()

    def event_close(self):
        self.end()


class Room(sge.dsp.Room):

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        self._font = font

    def event_step(self, time_passed, delta_mult):
        sge.game.project_text(self._font, "Hello, world!",
                              sge.game.width / 2,
                              sge.game.height / 2,
                              color=sge.gfx.Color("black"), halign="center",
                              valign="middle")
        pass
