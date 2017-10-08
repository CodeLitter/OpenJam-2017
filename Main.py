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
ROOM_WIDTH = VIEW_WIDTH * 2
ROOM_HEIGHT = 720
FLOOR_HEIGHT = 200
WALL_HEIGHT = ROOM_HEIGHT - FLOOR_HEIGHT
FLOOR_CENTER = WALL_HEIGHT + FLOOR_HEIGHT / 2
IMAGE_SPEED_FACTOR = 5
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
        self.z = self.y

    def event_step(self, time_passed, delta_mult):
        position = pygame.math.Vector2(self.x, self.y)

        if self.sprite is self.sprite_walk:
            if sge.mouse.get_pressed("left"):
                mouse_vec = pygame.math.Vector2(sge.game.mouse.x,
                                                sge.game.mouse.y)
                if position.distance_to(mouse_vec) > self.image_width / 6:
                    self.target.x = mouse_vec.x
                    self.target.y = mouse_vec.y
            self.z = self.y

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

    def is_hidden(self):
        return self.sprite is self.sprite_crouch

    def toggle_crouch(self, target_x, target_y):
        if self.sprite is self.sprite_walk:
            self.sprite = self.sprite_crouch
            self.target.x = target_x
            self.target.y = target_y
        else:
            self.sprite = self.sprite_walk

    def reset(self):
        self.x = self.xstart
        self.y = self.ystart
        self.xvelocity = 0
        self.yvelocity = 0
        self.target = pygame.math.Vector2(0, 0)


class Obstacle(sge.dsp.Object):

    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite=sprite,
                         image_origin_x=sprite.width / 2,
                         image_origin_y=sprite.height,
                         checks_collisions=True)

    def event_create(self):
        self.bbox_x -= self.image_origin_x
        self.bbox_y -= self.image_origin_y
        self.z = self.y

    def event_collision(self, other, xdirection, ydirection):
        if isinstance(other, Player):
            if Core.Game.key_pressed("space"):
                # TODO hide player
                target_x = self.x
                target_y = self.y
                other.toggle_crouch(target_x, target_y)
                other.z = self.z + math.copysign(10, self.y - FLOOR_CENTER)
                Core.Game.consume_key("space")


class Pet(sge.dsp.Object):

    def __init__(self, x, y, domain, turn_delay=1, move_speed=1):
        sprite = sge.gfx.Sprite(name="catWalk", directory=IMG_PATH)
        super().__init__(x, y, sprite=sprite,
                         image_origin_x=sprite.width / 2,
                         image_origin_y=sprite.height,
                         checks_collisions=True,
                         collision_precise=True)
        self.timer = 0
        self.domain = domain
        self.wait = turn_delay
        self.move_speed = move_speed

    def event_create(self):
        self.bbox_x = -self.image_origin_x
        self.bbox_y = -self.image_origin_y
        x_calc = self.x + self.domain
        self.x_begin = min(self.x, x_calc)
        self.x_end = max(self.x, x_calc)
        self.patrolling = True
        self.z = self.y

    def event_step(self, time_passed, delta_mult):
        # TODO if not chasing player patrol bewteen two points
        self.image_speed = IMAGE_SPEED_FACTOR * self.xvelocity * (time_passed / 1000)
        self.image_xscale = math.copysign(1, -self.xvelocity)
        if self.patrolling:
            if self.x <= self.x_begin or self.x >= self.x_end:
                if self.timer < self.wait:
                    self.timer += time_passed / 1000
                    self.x = Core.clamp(self.x, self.x_begin, self.x_end)
                    self.xvelocity = 0
                    self.image_index = 0
                else:
                    self.move_speed = -self.move_speed
                    self.xvelocity = self.move_speed
                    self.timer = 0
        else:
            pass

    def event_collision(self, other, xdirection, ydirection):
        if isinstance(other, Player):
            # TODO game over if player is not hidden
            if not other.is_hidden():
                sge.game.current_room.reset()
            pass

    def reset(self):
        self.x = self.xstart
        self.y = self.ystart
        self.xvelocity = 0
        self.yvelocity = 0
        self.timer = 0

class Victim(sge.dsp.Object):

    _SLEEP_DELAY = 5

    def __init__(self, x, y, player):
        self.player = player
        super().__init__(x, y, checks_collisions=True, collision_precise=True)


    def event_create(self):
        self.sprite_asleep = sge.gfx.Sprite(name="victimAsleep", directory=IMG_PATH)
        self.sprite_awake = sge.gfx.Sprite(name="victimAwake", directory=IMG_PATH)
        self.sprite = self.sprite_asleep
        self.image_origin_x = self.sprite.width
        self.image_origin_y = self.sprite.height
        self.bbox_x = -self.image_origin_x
        self.bbox_y = -self.image_origin_y
        self.bbox_width = self.sprite.width
        self.bbox_height = self.sprite.height
        self.z = self.y

    def event_step(self, time_passed, delta_mult):
        # TODO when timer runs out wake victim
        if sge.game.current_room.timer <= 0:
            if self.sprite is self.sprite_asleep:
                self.sprite = self.sprite_awake
                sge.game.current_room.timer = Victim._SLEEP_DELAY
            else:
                self.sprite = self.sprite_asleep
                sge.game.current_room.timer = sge.game.current_room.start_timer
        if self.sprite is self.sprite_awake:
            if not self.player.is_hidden():
                sge.game.current_room.reset()

    def event_collision(self, other, xdirection, ydirection):
        if isinstance(other, Player):
            # TODO end level and create a new room
            pass

    def reset(self):
        self.sprite = self.sprite_asleep

# Create Game object
Core.Game(width=VIEW_WIDTH,
          height=VIEW_HEIGHT,
          fps=60,
          window_text="Leave a mark",
          scale=1)

# Load Sprite
# TODO find out the order of sprite drawing

obstacle_sprites = []
for filename in glob.iglob(os.path.join(IMG_PATH, "obstacle_*.*")):
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
victim = Victim(ROOM_WIDTH, ROOM_HEIGHT, player=player)
pet = Pet(ROOM_WIDTH / 2, FLOOR_CENTER, -VIEW_WIDTH / 2)

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
                      background=background,
                      timer=30)
main_room.font = sge.gfx.Font()
sge.game.start_room = main_room

# sge.game.mouse.visible = False

if __name__ == "__main__":
    sge.game.start()
