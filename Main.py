#!/usr/bin/env python3
import sge
import pygame.math
import math
import glob
import ntpath
import os
import random
import Core

# Constants
VIEW_WIDTH = 1280
VIEW_HEIGHT = 720
ROOM_WIDTH = 2000
ROOM_HEIGHT = 720
FLOOR_HEIGHT = 200
IMG_PATH = "images"


class Player(sge.dsp.Object):

    def __init__(self, x, y, move_speed=1):
        super().__init__(x, y, collision_precise=True)
        self.move_speed = move_speed

    def event_create(self):
        self.sprite_walk = sge.gfx.Sprite(name="vampWalk", directory=IMG_PATH)
        self.sprite_crouch = sge.gfx.Sprite(name="vampCrouch", directory=IMG_PATH)
        self.sprite = self.sprite_walk
        self.image_origin_x = self.sprite.width / 2
        self.image_origin_y = self.sprite.height - 20
        self.target = pygame.math.Vector2(self.xstart, self.ystart)
        pass

    def event_step(self, time_passed, delta_mult):
        position = pygame.math.Vector2(self.x, self.y)

        if self.sprite is self.sprite_crouch:
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
        if self.sprite is self.sprite_walk:
            self.sprite = self.sprite_crouch
            self.target.x = target_x
            self.target.y = target_y
        else:
            self.sprite = self.sprite_walk


class Obstacle(sge.dsp.Object):

    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite=sprite,
                         image_origin_x=sprite.width / 2,
                         image_origin_y=sprite.height,
                         checks_collisions=True)
        self.bbox_x -= self.image_origin_x
        self.bbox_y -= self.image_origin_y

    def event_collision(self, other, xdirection, ydirection):
        if isinstance(other, Player):
            if Core.Game.key_pressed("space"):
                # TODO hide player
                other.toggle_crouch(self.x, self.y)


class Pet(sge.dsp.Object):
    timer = 0
    wait = 0
    pxone = 0
    pxtwo = 0
    dir = 1
    patrolling = False

    def __init__(self, x, y, patrol_x, wait_time):
        super().__init__(x, y, sprite=sge.gfx.Sprite(name="victimAwake", directory="images"),
                         image_origin_x=sprite.width / 2,
                         image_origin_y=sprite.height,
                         checks_collisions=True)
        self.bbox_y -= self.image_origin_x
        self.bbox_x -= self.image_origin_y
        self.pxone = x
        self.pxtwo = patrol_x
        self.wait = wait_time
        self.dir = 1 if x < patrol_x else -1

    def event_step(self, time_passed, delta_mult):
        # TODO if not chasing player patrol bewteen two points
        if self.patrolling == False:
            self.timer += 0.1

        if self.timer >= self.wait:
            # begin patrolling
            self.patrolling = True
            self.timer = 0
            self.dir *= -1

        if self.patrolling == True:
            if self.dir == 1:
                if self.x < self.pxtwo:
                    self.xvelocity = self.dir
                if self.x >= self.pxtwo:
                    self.xvelocity = 0
                    self.patrolling = False
            elif self.dir == -1:
                if self.x > self.pxone:
                    self.xvelocity = self.dir
                if self.x <= self.pxone:
                    self.xvelocity = 0
                    self.patrolling = False
        pass

    def event_collision(self, other, xdirection, ydirection):
        if type(other) is Player:
            # TODO game over if player is not hidden
            pass


class Victim(sge.dsp.Object):

    def __init__(self, x, y):
        super().__init__(x, y, checks_collisions=True)

    def event_create(self):
        self.sprite_asleep = sge.gfx.Sprite(name="victimAsleep", directory=IMG_PATH)
        # self.sprite_awake = sge.gfx.Sprite(name="victimAwake", directory=IMG_PATH)
        self.sprite = self.sprite_asleep
        self.image_origin_x = self.sprite.width
        self.image_origin_y = self.sprite.height
        self.bbox_y -= self.image_origin_x
        self.bbox_x -= self.image_origin_y

    def event_step(self, time_passed, delta_mult):
        # TODO when timer runs out wake victim
        pass

    def event_collision(self, other, xdirection, ydirection):
        if type(other) is Player:
            # TODO end level
            pass


# Create Game object
Core.Game(width=VIEW_WIDTH, height=VIEW_HEIGHT, fps=60, window_text="Leave a mark")

# Load Sprite
# TODO find out the order of sprite drawing

obstacle_sprites = []
for filename in glob.iglob(os.path.join(IMG_PATH, "lounge*.*")):
    filename = ntpath.basename(filename).split('.')[0]
    sprite = sge.gfx.Sprite(filename, directory=IMG_PATH)
    obstacle_sprites.append(sprite)

background_sprites = []
for filename in glob.iglob(os.path.join(IMG_PATH, "wallPanel*.*")):
    filename = ntpath.basename(filename).split('.')[0]
    sprite = sge.gfx.Sprite(filename, directory=IMG_PATH)
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
main_view = sge.dsp.View(0, 0, width=VIEW_WIDTH, height=VIEW_HEIGHT)

# Create Objects
objects = []
player = Player(-300, ROOM_HEIGHT, move_speed=3)
victim = Victim(ROOM_WIDTH, ROOM_HEIGHT)
pet = Pet(500, ROOM_HEIGHT, 800, 1)

objects.append(player)
objects.append(victim)
objects.append(pet)
objects.extend([Obstacle(count * 320,  # obstacle_sprites[0].width,
                         ROOM_HEIGHT - random.randrange(FLOOR_HEIGHT),
                         random.choice(obstacle_sprites))
                for count in range(1, 5)])

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
