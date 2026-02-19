
import sys

import arcade
from arcade import Camera2D
from pyglet.graphics import Batch

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Further and further Runner"
TILE_SCALING = 0.5
GRAVITY = 0.5
PLAYER_SPEED = 6
CAMERA_LERP = 0.12
MAX_JUMPS = 1
JUMP_BUFFER = 0.12
JUMP_SPEED = 20
COYOTE_TIME = 0.08


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.SPANISH_SKY_BLUE)

        self.left = False
        self.right = False
        self.jumps_left = MAX_JUMPS
        self.time_since_ground = 0
        self.jump_buffer_timer = 0
        self.up = False
        self.down = False
        self.jump_pressed = False

        self.spawn_point = 140, 140

        self.player = arcade.Sprite(
            ':resources:/images/animated_characters/female_adventurer/femaleAdventurer_idle.png',
            TILE_SCALING,
            *self.spawn_point
        )

        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        try:
            tilemap = arcade.load_tilemap('further_and_further.tmx', TILE_SCALING)
        except Exception:
            print('Убедитесь, что further_and_further.tmx и collection.tsx находятся в одной папке с исполняемым файлом'
                  ', а tiles.png в папке assets')
            sys.exit()

        self.ground_list = tilemap.sprite_lists['ground']
        self.ladders_list = tilemap.sprite_lists['ladders']
        self.lava_water_list = tilemap.sprite_lists['lava_water']
        self.platforms_list = tilemap.sprite_lists['platforms']
        self.collisions = tilemap.sprite_lists['collisions']
        self.keys_list = arcade.SpriteList()
        self.hazard_list = arcade.SpriteList()

        self.visible_lists = [
            self.ground_list,
            self.ladders_list,
            self.lava_water_list,
            self.platforms_list,
            self.player_list,
            self.keys_list,
        ]

        for hazard in self.lava_water_list.sprite_list[2:]:
            self.hazard_list.append(hazard)
        self.keys_list.append(arcade.Sprite(':resources:images/items/keyYellow.png', TILE_SCALING, 140, 700))
        self.keys_list.append(arcade.Sprite(':resources:images/items/keyYellow.png', TILE_SCALING, 1020, 140))
        self.keys_list.append(arcade.Sprite(':resources:images/items/keyYellow.png', TILE_SCALING, 450, 140))
        self.keys_list.append(arcade.Sprite(':resources:images/items/keyYellow.png', TILE_SCALING, 500, 700))
        self.keys_list.append(arcade.Sprite(':resources:images/items/keyYellow.png', TILE_SCALING, 1500, 666))

        # Физический движок
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.platforms_list,
            ladders=self.ladders_list,
            walls=self.ground_list,
        )

        self.batch = Batch()
        self.score = 0

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        for item in self.visible_lists:
            item.draw()

        any_key_text = arcade.Text(f"Score: {self.score}",
                                   0, self.height - 25,
                                   arcade.color.PURPLE, font_size=20, anchor_x="left", batch=self.batch)

        self.gui_camera.use()
        self.batch.draw()
    def on_update(self, dt: float):
        # Обработка горизонтального движения
        move = 0
        if self.left and not self.right:
            move = -PLAYER_SPEED
        elif self.right and not self.left:
            move = PLAYER_SPEED
        self.player.change_x = move

        on_ladder = self.physics_engine.is_on_ladder()  # На лестнице?
        if on_ladder:
            # По лестнице вверх/вниз
            if self.up and not self.down:
                self.player.change_y = PLAYER_SPEED
            elif self.down and not self.up:
                self.player.change_y = -PLAYER_SPEED
            else:
                self.player.change_y = 0

        # Прыжок: can_jump() + койот + буфер
        grounded = self.physics_engine.can_jump(y_distance=6)  # Есть пол под ногами?
        if grounded:
            self.time_since_ground = 0
            self.jumps_left = MAX_JUMPS
        else:
            self.time_since_ground += dt

        # Учтём «запомненный» пробел
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= dt

        want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)

        # Можно прыгать, если стоим на земле или в пределах койот-времени
        if want_jump:
            can_coyote = (self.time_since_ground <= COYOTE_TIME)
            if grounded or can_coyote:
                # Просим движок прыгнуть: он корректно задаст начальную вертикальную скорость
                self.physics_engine.jump(JUMP_SPEED)
                self.jump_buffer_timer = 0

        # Обновляем физику — движок сам двинет игрока и платформы
        self.physics_engine.update()

        if arcade.check_for_collision_with_list(self.player, self.hazard_list) or self.player.center_y < -50:
            self.player.center_x, self.player.center_y = self.spawn_point
            self.player.change_x = self.player.change_y = 0
            self.time_since_ground = 999
            self.jumps_left = MAX_JUMPS

        for key in arcade.check_for_collision_with_list(self.player, self.keys_list):
            key.kill()
            self.score += 1

        # Камера — плавно к игроку и в рамках мира
        target = (self.player.center_x, self.player.center_y)
        cx, cy = self.world_camera.position
        smooth = (cx + (target[0] - cx) * CAMERA_LERP,
                  cy + (target[1] - cy) * CAMERA_LERP)

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        # Ограничим, чтобы за края уровня не выглядывало небо
        world_w = 70 * 30  # Мы руками построили пол до x = 2000
        world_h = 1920
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_h, smooth[1]))

        self.world_camera.position = (cam_x, cam_y)

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = True
        elif key == arcade.key.SPACE:
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = False
        elif key == arcade.key.SPACE:
            self.jump_pressed = False
            # Вариативная высота прыжка: отпустили рано — подрежем скорость вверх
            if self.player.change_y > 0:
                self.player.change_y *= 0.45


def setup_game(width=768, height=450, title="Moving Platforms Runner"):
    game = MyGame(width, height, title)
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
