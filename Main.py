#!/usr/bin/env python3
import sge
import pygame.math
import math
import glob
import os
import json
import Core
import Rooms


# Constants
VIEW_WIDTH = 1280
VIEW_HEIGHT = 720
ROOM_WIDTH = VIEW_WIDTH * 2
ROOM_HEIGHT = 720
FLOOR_HEIGHT = 200
WALL_HEIGHT = ROOM_HEIGHT - FLOOR_HEIGHT
FLOOR_CENTER = WALL_HEIGHT + FLOOR_HEIGHT / 2
IMAGE_SPEED_FACTOR = 5


def create_objects(path):
    with open(path) as file:
        attributes = json.load(file)
        objects = []
        for _type in attributes:
            obj = eval(_type)(**attributes[_type])
            objects.append(obj)
        return objects


class Player(sge.dsp.Object):

    def __init__(self, move_speed=1, **kwargs):
        super().__init__(collision_precise=True, **kwargs)
        self.move_speed = move_speed

    def event_create(self):
        self.sprite_walk = sge.gfx.Sprite(name="vampWalk",
                                          directory=Core.IMG_PATH)
        self.sprite_crouch = sge.gfx.Sprite(name="vampCrouch",
                                            directory=Core.IMG_PATH)
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

    def __init__(self, x, y, sprite_name):
        if sprite_name not in Core.Game.sprites:
            sprite = sge.gfx.Sprite(sprite_name, directory=Core.IMG_PATH)
            Core.Game.sprites[sprite_name] = sprite
        else:
            sprite = Core.Game.sprites.sprites[sprite_name]
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

    sprites = {}

    def __init__(self, x, y, domain, sprite_name="catWalk", turn_delay=1, move_speed=1):
        if sprite_name not in Core.Game.sprites:
            sprite = sge.gfx.Sprite(sprite_name, directory=Core.IMG_PATH)
            Core.Game.sprites[sprite_name] = sprite
        else:
            sprite = Core.Game.sprites[sprite_name]
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
                sge.game.current_room.play_sound(os.path.join(Core.SND_PATH, "tomcat.ogg"))
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

    def __init__(self, x, y):
        self.player = None
        super().__init__(x, y, checks_collisions=True, collision_precise=True)

    def event_create(self):
        self.sprite_asleep = sge.gfx.Sprite(name="victimAsleep",
                                            directory=Core.IMG_PATH)
        self.sprite_awake = sge.gfx.Sprite(name="victimAwake",
                                           directory=Core.IMG_PATH)
        self.player = next(filter(lambda x: isinstance(x, Player),
                                  sge.game.current_room.objects),
                           None)
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
                view = next(iter(sge.game.current_room.views))
                if abs(self.x - self.player.x) < view.width:
                    sge.game.current_room.reset()

    def event_collision(self, other, xdirection, ydirection):
        if isinstance(other, Player):
            # TODO end level and create a new room
            room = sge.game.next_room()
            if room is not None:
                room.start()
            else:
                sge.game.end()

    def reset(self):
        self.sprite = self.sprite_asleep


class TransitionButton(sge.dsp.Object):

    def __init__(self, x, y, sprite_name, room_index):
        if sprite_name not in Core.Game.sprites:
            sprite = sge.gfx.Sprite(sprite_name, directory=Core.IMG_PATH)
            Core.Game.sprites[sprite_name] = sprite
        else:
            sprite = Core.Game.sprites[sprite_name]
        super().__init__(x, y, sprite=sprite, checks_collisions=True)
        self.room_index = room_index
        self.sprite_normal = self.sprite
        sprite_name_clicked = sprite_name + '_clicked'
        if sprite_name_clicked not in Core.Game.sprites:
            self.sprite_clicked = sge.gfx.Sprite(sprite_name_clicked, directory=Core.IMG_PATH)
            Core.Game.sprites[sprite_name_clicked] = self.sprite_clicked
        else:
            self.sprite_clicked = Core.Game.sprites[sprite_name_clicked]

        sprite_name_hover = sprite_name + '_hover'
        if sprite_name_hover not in Core.Game.sprites:
            self.sprite_hover = sge.gfx.Sprite(sprite_name_hover, directory=Core.IMG_PATH)
            Core.Game.sprites[sprite_name_hover] = self.sprite_hover
        else:
            self.sprite_hover = Core.Game.sprites[sprite_name_hover]

    def event_step(self, time_passed, delta_mult):
        self.sprite = self.sprite_normal

    def event_collision(self, other, xdirection, ydirection):
        if isinstance(other, sge.dsp.Mouse):
            self.sprite = self.sprite_hover
            if sge.mouse.get_pressed("left"):
                self.sprite = self.sprite_clicked
                room = sge.game.get_room(self.room_index)
                room.start()


# TODO move creation code to an initialization file
def main():
    # Create Game object
    Core.Game.config_create("config.json")

    # Load fonts
    font = sge.gfx.Font()

    #==New Shit To Look At=================================================
    # # create menu sprites
    # play_sprite = sge.gfx.Sprite("playButton.png", Core.IMG_PATH)
    # instructions_sprite = sge.gfx.Sprite("instructButton.png", Core.IMG_PATH)
    # credits_sprite = sge.gfx.Sprite("creditsButton.png", Core.IMG_PATH)
    #
    # # create menu objects
    # menu_objects = []
    # play_button = sge.dsp.Object(524, 400, play_sprite)
    # instructions_button = sge.dsp.Object(9, 400, instructions_sprite)
    # credits_button = sge.dsp.Object(984, 400, credits_sprite)
    #
    # menu_objects.append(play_button)
    # menu_objects.append(instructions_button)
    # menu_objects.append(credits_button)
    #
    # # create menu room
    # menu_room = sge.dsp.Room(menu_objects,
    #                          ROOM_WIDTH/2,
    #                          ROOM_HEIGHT,
    #                          sge.dsp.View,
    #                          #NEED_A_BACKGROUND
    #                          )
    #==New Shit To Look At=================================================

    # Create rooms
    for path in sorted(glob.iglob(os.path.join("rooms", "*.json"))):
        filename = os.path.basename(path)
        objects = create_objects(os.path.join("objects", filename))
        room = Rooms.create_room(path, font=font, objects=objects,
                                 views=[sge.game.view])
        sge.game.rooms.append(room)

    sge.game.start_room = sge.game.next_room()
    sge.game.start()


if __name__ == "__main__":
    main()
