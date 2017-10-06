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

        # sge.game.project_text(font, "Hello, world!",
        #                       sge.game.width / 2,
        #                       sge.game.height / 2,
        #                       color=sge.gfx.Color("black"), halign="center",
        #                       valign="middle")
        pass


class Player(sge.dsp.Object):
    def __init__(self):
        super().__init__(0, 0, sprite=sprite, checks_collisions=True)

    def event_step(self, time_passed, delta_mult):
        pass


# Create Game object
Game(width=1280, height=720, fps=60, window_text="Leave a mark")

# Create backgrounds
background = sge.gfx.Background([], sge.gfx.Color("white"))

# Load fonts
font = sge.gfx.Font()

# Load Sprite
sprite = sge.gfx.Sprite(name="SingleNosferatu", directory="images")

# Create Player
player = Player()

objects = [player]

# Create rooms
sge.game.start_room = Room(objects, background=background)

if __name__ == "__main__":
    sge.game.start()
