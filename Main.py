#!/usr/bin/env python3
import sge
import pygame.math
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
        if sge.mouse.get_pressed("left"):
            self._target.x = sge.game.mouse.x
            self._target.y = sge.game.mouse.y

        position = pygame.math.Vector2(self.x, self.y)
        if (self._target.distance_to(position) > self.move_speed + 0.1):
            direction = self.move_speed * (self._target - position).normalize()
            self.xvelocity = direction.x
            self.yvelocity = direction.y
            self.image_speed = self.move_speed * (time_passed / 1000)
        else:
            self.xvelocity = 0
            self.yvelocity = 0
            self.image_speed = 0
            self.image_index = 0
        sge.game.current_room.views[0].x = (self.x - sge.game.width/2)
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

# Create backgrounds
background_sprites = sge.gfx.Sprite("victimAsleep", directory="images")
layer = sge.gfx.BackgroundLayer(background_sprites, 0, 0, repeat_right=True)
background = sge.gfx.Background([layer], sge.gfx.Color("white"))

# Load fonts

# Load Sprite
sprite_player = sge.gfx.Sprite(name="vampWalk",
                               directory="images")

sprite_goal = sge.gfx.Sprite(name="victimAsleep",
                             directory="images")

# Create View
main_view = sge.dsp.View(0, 0,
                         width=sge.game.width)

# Create Player
player = Player(5)

objects = [player, Goal()]

# Create rooms
main_room = Core.Room(objects,
                      views=[main_view],
                      width=sge.game.width * 2,
                      background=background)
main_room.font = sge.gfx.Font()
sge.game.start_room = main_room

# sge.game.mouse.visible = False

if __name__ == "__main__":
    sge.game.start()
