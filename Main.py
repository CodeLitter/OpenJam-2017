#!/usr/bin/env python3
import sge
import pygame.math
import math
import glob
import ntpath
import random
from pathlib import Path
import Core


class Player(sge.dsp.Object):

    def __init__(self, move_speed=1):
        super().__init__(sge.game.width/2,
                         sge.game.height/2,
                         sprite=sprite_player,
                         image_origin_x=sprite_player.width/2,
                         image_origin_y=sprite_player.height/2,
                         checks_collisions=True)
        self.move_speed = move_speed
        self._target = pygame.math.Vector2(self.xstart, self.ystart)

    def event_step(self, time_passed, delta_mult):
        position = pygame.math.Vector2(self.x, self.y)
        floor_height = 200

        if sge.mouse.get_pressed("left"):
            mouse_vec = pygame.math.Vector2(sge.game.mouse.x,
                                            sge.game.mouse.y)
            if position.distance_to(mouse_vec) > self.image_width / 2:
                self._target.x = mouse_vec.x
                self._target.y = mouse_vec.y

        game_offset_height = sge.game.height - self.image_height / 2
        self._target.y = Core.clamp(self._target.y,
                                    game_offset_height - floor_height,
                                    game_offset_height)
        if position.distance_to(self._target) > self.move_speed + 0.1:
            direction = self.move_speed * (self._target - position).normalize()
            self.xvelocity = direction.x
            self.yvelocity = direction.y
            self.image_speed = self.move_speed * (time_passed / 1000)
        else:
            self.xvelocity = 0
            self.yvelocity = 0
            self.image_speed = 0
            self.image_index = 0
        self.image_xscale = math.copysign(1, self.xvelocity)
        sge.game.current_room.views[0].x = (self.x - sge.game.width / 2)
        pass


class Goal(sge.dsp.Object):

    def __init__(self):
        super().__init__(sge.game.width/2,
                         sge.game.height/2,
                         sprite=sprite_goal,
                         image_origin_x=sprite_goal.width/2,
                         image_origin_y=sprite_goal.height/2,
                         checks_collisions=True)
        pass

    def event_step(self, time_passed, delta_mult):
        pass


# Create Game object
Core.Game(width=1280, height=720, fps=60, window_text="Leave a mark")
ROOM_WIDTH = sge.game.width * 2

# Load Sprite
sprite_player = sge.gfx.Sprite(name="vampWalk",
                               directory="images")
sprite_goal = sge.gfx.Sprite(name="victimAsleep",
                             directory="images")
background_sprites = []
for filename in glob.iglob("./images/wallPanel*.*"):
    filename = ntpath.basename(filename).split('.')[0]
    sprite = sge.gfx.Sprite(filename, directory="images")
    background_sprites.append(sprite)

# Create backgrounds
layers = []
for offset in range(int(ROOM_WIDTH / background_sprites[0].width)):
    index = random.randrange(len(background_sprites))
    sprite = background_sprites[index]
    layer = sge.gfx.BackgroundLayer(sprite, offset * sprite.width, 0)
    layers.append(layer)

background = sge.gfx.Background(layers, sge.gfx.Color("white"))

# Load fonts


# Create View
main_view = sge.dsp.View(0, 0, width=sge.game.width)

# Create Player
player = Player(3)

objects = [player, Goal()]

# Create rooms
main_room = Core.Room(objects,
                      views=[main_view],
                      width=ROOM_WIDTH,
                      background=background)
main_room.font = sge.gfx.Font()
sge.game.start_room = main_room

# sge.game.mouse.visible = False

if __name__ == "__main__":
    sge.game.start()
