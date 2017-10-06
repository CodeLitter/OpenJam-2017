#!/usr/bin/env python3
import sge
import Core


class Player(sge.dsp.Object):
    def __init__(self):
        super().__init__(0, 0, sprite=sprite_player, checks_collisions=True)

    def event_step(self, time_passed, delta_mult):
        pass


# Create Game object
Core.Game(width=1280, height=720, fps=60, window_text="Leave a mark")

# Create backgrounds
background = sge.gfx.Background([], sge.gfx.Color("white"))

# Load fonts
# main.add_font(sge.gfx.Font())

# Load Sprite
sprite_player = sge.gfx.Sprite(name="SingleNosferatu", directory="images")

# Create Player
player = Player()

objects = [player]

# Create rooms
main_room = Core.Room(objects, background=background)
main_room.font = sge.gfx.Font()
sge.game.start_room = main_room

sge.game.mouse.visible = False

if __name__ == "__main__":
    sge.game.start()
