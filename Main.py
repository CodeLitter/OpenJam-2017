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
        super().__init__(x, y, sprite=sprite_player_walk,
                         image_origin_x=sprite_player_walk.width/2,
                         image_origin_y=sprite_player_walk.height - 20,
                         collision_precise=True)
        self.move_speed = move_speed
        self.target = pygame.math.Vector2(self.xstart, self.ystart)

    def event_step(self, time_passed, delta_mult):
        position = pygame.math.Vector2(self.x, self.y)

        if self.sprite is sprite_player_crouch:
            pass
        elif sge.mouse.get_pressed("left"):
            mouse_vec = pygame.math.Vector2(sge.game.mouse.x,
                                            sge.game.mouse.y)
            if position.distance_to(mouse_vec) > self.image_width / 6:
                self.target.x = mouse_vec.x
                self.target.y = mouse_vec.y
        self.target.x = Core.clamp(self.target.x,
                                   self.image_width / 2,
                                   ROOM_WIDTH - self.image_width / 2)
        self.target.y = Core.clamp(self.target.y,
                                   sge.game.height - FLOOR_HEIGHT,
                                   sge.game.height)

        if position.distance_to(self.target) > self.move_speed + 0.1:
            direction = self.move_speed * (self.target - position).normalize()
            self.xvelocity = direction.x
            self.yvelocity = direction.y
            self.image_speed = self.move_speed * (time_passed / 1000)
        else:
            self.xvelocity = 0
            self.yvelocity = 0
            self.image_speed = 0
            self.image_index = 0
        # Flip sprite to face direction
        self.image_xscale = math.copysign(1, self.xvelocity)
        # adjust view to player's position
        sge.game.current_room.views[0].x = (self.x - sge.game.width / 4)
        pass

    def toggle_crouch(self, target_x, target_y):
        if self.sprite is sprite_player_walk:
            self.sprite = sprite_player_crouch
            self.target.x = target_x
            self.target.y = target_y
        else:
            self.sprite = sprite_player_walk


class Obstacle(sge.dsp.Object):

    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite=sprite,
                         image_origin_x=sprite.width / 2,
                         image_origin_y=sprite.height,
                         checks_collisions=True,
                         collision_ellipse=True)
        self.bbox_y -= self.image_origin_x
        self.bbox_x -= self.image_origin_y

    def event_collision(self, other, xdirection, ydirection):
        if isinstance(other, Player):
            if Core.Game.key_pressed("space"):
                # TODO hide player
                other.toggle_crouch(self.x, self.y)


class Pet(sge.dsp.Object):

    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite=sprite,
                         image_origin_x=sprite.width / 2,
                         image_origin_y=sprite.height,
                         checks_collisions=True)
        self.bbox_y -= self.image_origin_x
        self.bbox_x -= self.image_origin_y

    def event_collision(self, other, xdirection, ydirection):
        if type(other) is Player:
            # TODO game over
            pass


class Victim(sge.dsp.Object):

    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite=sprite,
                         image_origin_x=sprite.width,
                         image_origin_y=sprite.height,
                         checks_collisions=True)
        self.bbox_y -= self.image_origin_x
        self.bbox_x -= self.image_origin_y

    def event_collision(self, other, xdirection, ydirection):
        if type(other) is Player:
            # TODO end level
            pass


# Create Game object
Core.Game(width=1280, height=720, fps=60, window_text="Leave a mark")
ROOM_WIDTH = sge.game.width * 2
FLOOR_HEIGHT = 200

# Load Sprite
sprite_player_walk = sge.gfx.Sprite(name="vampWalk",
                                    directory="images")
sprite_player_crouch = sge.gfx.Sprite(name="vampCrouch",
                                      directory="images")
sprite_victim = sge.gfx.Sprite(name="victimAsleep",
                               directory="images")

obstacle_sprites = []
for filename in glob.iglob("./images/tableWquill*.*"):
    filename = ntpath.basename(filename).split('.')[0]
    sprite = sge.gfx.Sprite(filename, directory="images")
    obstacle_sprites.append(sprite)

background_sprites = []
for filename in glob.iglob("./images/wallPanel*.*"):
    filename = ntpath.basename(filename).split('.')[0]
    sprite = sge.gfx.Sprite(filename, directory="images")
    background_sprites.append(sprite)


# Create backgrounds
layers = []
for offset in range(int(ROOM_WIDTH / background_sprites[0].width)):
    layer = sge.gfx.BackgroundLayer(None, offset * sprite.width, 0)
    layers.append(layer)

Core.randomize_layers(layers, background_sprites)

background = sge.gfx.Background(layers, sge.gfx.Color("white"))

# Load fonts


# Create View
main_view = sge.dsp.View(0, 0, width=sge.game.width)

# Create Objects
objects = []
player = Player(-sprite_player_walk.width, main_view.height, move_speed=3)
victim = Victim(ROOM_WIDTH, main_view.height, sprite_victim)

objects.append(player)
objects.append(victim)
objects.extend([Obstacle(count * 320,  # obstacle_sprites[0].width,
                         main_view.height - random.randrange(FLOOR_HEIGHT),
                         random.choice(obstacle_sprites))
                for count in range(5)])

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
