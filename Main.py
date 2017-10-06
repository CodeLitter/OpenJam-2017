#!/usr/bin/env python3
import sge


class Game(sge.dsp.Game):

    def event_key_press(self, key, char):
        if key == 'escape':
            self.event_close()

    def event_close(self):
        self.end()


class Room(sge.dsp.Room):

    def event_step(self, time_passed, delta_mult):
        sge.game.project_text(font, "Hello, world!",
                              sge.game.width / 2,
                              sge.game.height / 2,
                              color=sge.gfx.Color("black"), halign="center",
                              valign="middle")


# Create Game object
Game()

# Create backgrounds
background = sge.gfx.Background([], sge.gfx.Color("white"))

# Load fonts
font = sge.gfx.Font()

# Create rooms
sge.game.start_room = Room(background=background)

if __name__ == "__main__":
    sge.game.start()
