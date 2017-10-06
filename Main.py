#!/usr/bin/env python3
import sge
import pygame.math
import Core


class Player(sge.dsp.Object):

    def __init__(self, speed=1):
        super().__init__(0, 0, sprite=sprite_player, checks_collisions=True)
        self.speed = speed
        self._target = pygame.math.Vector2(self.xstart, self.ystart)

    def event_step(self, time_passed, delta_mult):
        if sge.mouse.get_pressed("left"):
            self._target.x = sge.game.mouse.x
            self._target.y = sge.game.mouse.y

        position = pygame.math.Vector2(self.x, self.y)
        if (self._target.distance_to(position) > self.speed + 0.1):
            direction = self.speed * (self._target - position).normalize()
            self.xvelocity = direction.x
            self.yvelocity = direction.y
        else:
            self.x = self._target.x
            self.y = self._target.y

        pass


# Create Game object
Core.Game(width=1280, height=720, fps=60, window_text="Leave a mark")

# Create backgrounds
background = sge.gfx.Background([], sge.gfx.Color("white"))

# Load fonts

# Load Sprite
sprite_player = sge.gfx.Sprite(name="SingleNosferatu",
                               directory="images",
                               origin_x=128,
                               origin_y=128)

# Create Player
player = Player()

objects = [player]

# Create rooms
main_room = Core.Room(objects, background=background)
main_room.font = sge.gfx.Font()
sge.game.start_room = main_room

#sge.game.mouse.visible = False

if __name__ == "__main__":
    sge.game.start()
