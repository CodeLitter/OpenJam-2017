#!/usr/bin/env python3
import sge
import pygame.math
import math
import glob
import ntpath
import random
import Core


class Player(sge.dsp.Object):

    def __init__(self, x, y, move_speed=1):
        super().__init__(x, y, sprite=sprite_player,
                         image_origin_x=sprite_player.width/2,
                         image_origin_y=sprite_player.height - 20,
                         checks_collisions=True,
                         collision_precise=True)
        self.move_speed = move_speed
        self._target = pygame.math.Vector2(self.xstart, self.ystart)

    def event_step(self, time_passed, delta_mult):
        position = pygame.math.Vector2(self.x, self.y)

        # Debug
        if sge.keyboard.get_pressed("space"):
            randomize_layers(layers)
        # End Debug

        if sge.mouse.get_pressed("left"):
            mouse_vec = pygame.math.Vector2(sge.game.mouse.x,
                                            sge.game.mouse.y)
            if position.distance_to(mouse_vec) > self.image_width / 6:
                self._target.x = mouse_vec.x
                self._target.y = mouse_vec.y
        self._target.x = Core.clamp(self._target.x,
                                    self.image_width / 2,
                                    ROOM_WIDTH - self.image_width / 2)
        self._target.y = Core.clamp(self._target.y,
                                    sge.game.height - FLOOR_HEIGHT,
                                    sge.game.height)
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


class Victim(sge.dsp.Object):

    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite=sprite,
                         image_origin_x=sprite.width,
                         image_origin_y=sprite.height,
                         checks_collisions=True,
                         collision_precise=True)
    pass

    def event_collision(self, other, xdirection, ydirection):
        if type(other) is Player:
            print(other)
            # sge.game.event_close()
            pass


# Create Game object
Core.Game(width=1280, height=720, fps=60, window_text="Leave a mark")
ROOM_WIDTH = sge.game.width * 2
FLOOR_HEIGHT = 200

# Load Sprite
sprite_player = sge.gfx.Sprite(name="vampWalk",
                               directory="images")
sprite_victim = sge.gfx.Sprite(name="victimAsleep",
                               directory="images")
background_sprites = []
for filename in glob.iglob("./images/wallPanel*.*"):
    filename = ntpath.basename(filename).split('.')[0]
    sprite = sge.gfx.Sprite(filename, directory="images")
    background_sprites.append(sprite)


# Create backgrounds
def randomize_layers(layers):
    for layer in layers:
        index = random.randrange(len(background_sprites))
        sprite = background_sprites[index]
        layer.sprite = sprite


layers = []
for offset in range(int(ROOM_WIDTH / background_sprites[0].width)):
    layer = sge.gfx.BackgroundLayer(None, offset * sprite.width, 0)
    layers.append(layer)

randomize_layers(layers)

background = sge.gfx.Background(layers, sge.gfx.Color("white"))

# Load fonts


# Create View
main_view = sge.dsp.View(0, 0, width=sge.game.width)

# Create Player
player = Player(-sprite_player.width, main_view.height, move_speed=3)

objects = [player,
           Victim(ROOM_WIDTH, main_view.height, sprite_victim)]

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
