import random

import arcade
from pyglet.graphics import Batch

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Castle Camera"
TILE_SCALING = 1.0
TILE_SIZE = 70
SPEED = 14
CAMERA_LERP = 0.12
# Размеры мёртвой зоны камеры
DEAD_ZONE_W = int(SCREEN_WIDTH * 0.35)
DEAD_ZONE_H = int(SCREEN_HEIGHT * 0.45)


class StartView(arcade.View):
    def on_show(self):
        """Настройка начального экрана"""
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """Отрисовка начального экрана"""
        self.clear()

        # Батч для текста
        self.batch = Batch()
        start_text = arcade.Text("Заколдованный замок", self.window.width / 2, self.window.height / 2,
                                 arcade.color.WHITE, font_size=50, anchor_x="center", batch=self.batch)
        any_key_text = arcade.Text("Any key to start",
                                   self.window.width / 2, self.window.height / 2 - 75,
                                   arcade.color.GRAY, font_size=20, anchor_x="center", batch=self.batch)

        self.batch.draw()

    def on_key_press(self, key, modifiers):
        """Начало игры при нажатии клавиши"""
        self.window.show_view(LevelFirst())


class LevelFirst(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.shaker = arcade.camera.grips.ScreenShake2D(
            self.world_camera.view_data,
            max_amplitude=12,
            acceleration_duration=0.1,
            falloff_time=0.5,
            shake_frequency=10
        )

        # Инициализируем списки спрайтов
        self.player = arcade.Sprite(
            ':resources:images/animated_characters/robot/robot_idle.png', TILE_SCALING,
            self.center_x, self.center_y / 2
        )

        # Инициализируем списки спрайтов
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.gems_list = arcade.SpriteList()

        # ===== ВОЛШЕБСТВО ЗАГРУЗКИ КАРТЫ! (почти без магии) =====
        # Грузим тайловую карту
        map_name = "assets/castle_map.tmx"
        # Параметр 'scaling' ОЧЕНЬ важен! Умножает размер каждого тайла
        tile_map = arcade.load_tilemap(map_name, TILE_SCALING)

        # --- Достаём слои из карты как спрайт-листы ---
        self.castle_list = tile_map.sprite_lists["castle"]
        self.windows_list = tile_map.sprite_lists["windows"]
        self.yard_list = tile_map.sprite_lists["yard"]
        self.fence_list = tile_map.sprite_lists["fence"]
        self.stones_list = tile_map.sprite_lists["stones"]

        self.visible_lists = [
            self.castle_list,
            self.windows_list,
            self.yard_list,
            self.fence_list,
            self.stones_list,
            self.player_list,
            self.gems_list,
        ]

        self.collisions_list = tile_map.sprite_lists["collisions"]

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.collisions_list
        )

        # Кристаллы
        for _ in range(random.randint(10, 15)):
            self.gems_list.append(arcade.Sprite(
                ':resources:images/items/gemBlue.png', TILE_SCALING / 3,
                                                       70 * random.randint(1 + 1, 14 - 1),
                                                       70 * random.randint(1 + 1, 6 - 1)
            ))
        self.gems = len(self.gems_list)

        self.batch = Batch()

    def on_draw(self):
        """Отрисовка экрана"""
        self.clear()
        self.shaker.update_camera()
        self.world_camera.use()
        # Рисуем слои карты в правильном порядке
        for visible in self.visible_lists:
            visible.draw()
        self.shaker.readjust_camera()

        any_key_text = arcade.Text(f"Score: {self.gems - len(self.gems_list)}",
                                   0, self.window.height - 25,
                                   arcade.color.PURPLE, font_size=20, anchor_x="left", batch=self.batch)

        self.gui_camera.use()
        self.batch.draw()

    def on_update(self, delta_time: float):
        self.physics_engine.update()
        self.shaker.update(delta_time)

        for gem in arcade.check_for_collision_with_list(self.player, self.gems_list):
            gem.kill()
            self.shaker.start()

        if len(self.gems_list) == 0:
            second_level = LevelSecond()
            self.window.show_view(second_level)

        cam_x, cam_y = self.world_camera.position
        dz_left = cam_x - DEAD_ZONE_W // 2
        dz_right = cam_x + DEAD_ZONE_W // 2
        dz_bottom = cam_y - DEAD_ZONE_H // 2
        dz_top = cam_y + DEAD_ZONE_H // 2

        px, py = self.player.center_x, self.player.center_y
        target_x, target_y = cam_x, cam_y

        if px < dz_left:
            target_x = px + DEAD_ZONE_W // 2
        elif px > dz_right:
            target_x = px - DEAD_ZONE_W // 2
        if py < dz_bottom:
            target_y = py + DEAD_ZONE_H // 2
        elif py > dz_top:
            target_y = py - DEAD_ZONE_H // 2

        # Не показываем «пустоту» за краями карты
        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        target_x = max(half_w, min(1050 - half_w, target_x))
        target_y = max(half_h, min(700 - half_h, target_y))

        # Плавно к цели, аналог arcade.math.lerp_2d, но руками
        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y
        self.cam_target = (smooth_x, smooth_y)

        self.world_camera.position = (self.cam_target[0], self.cam_target[1])

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.change_x = -SPEED
        if key == arcade.key.RIGHT:
            self.player.change_x = SPEED
        if key == arcade.key.DOWN:
            self.player.change_y = -SPEED
        if key == arcade.key.UP:
            self.player.change_y = SPEED

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.change_x = 0
        if key == arcade.key.RIGHT:
            self.player.change_x = 0
        if key == arcade.key.DOWN:
            self.player.change_y = 0
        if key == arcade.key.UP:
            self.player.change_y = 0


'----------------------------------------------------------------------------------------------------------------------'


class LevelSecond(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.shaker = arcade.camera.grips.ScreenShake2D(
            self.world_camera.view_data,
            max_amplitude=12,
            acceleration_duration=0.1,
            falloff_time=0.5,
            shake_frequency=10
        )

        # Инициализируем списки спрайтов.
        self.player = arcade.Sprite(
            ':resources:images/animated_characters/robot/robot_idle.png', TILE_SCALING,
            self.center_x, self.center_y / 2
        )

        # Инициализируем списки спрайтов
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.gems_list = arcade.SpriteList()

        # ===== ВОЛШЕБСТВО ЗАГРУЗКИ КАРТЫ! (почти без магии) =====
        # Грузим тайловую карту
        map_name = "assets/castle_map.tmx"
        # Параметр 'scaling' ОЧЕНЬ важен! Умножает размер каждого тайла
        tile_map = arcade.load_tilemap(map_name, TILE_SCALING)

        # --- Достаём слои из карты как спрайт-листы ---
        self.castle_list = tile_map.sprite_lists["castle"]
        self.windows_list = tile_map.sprite_lists["windows"]
        self.yard_list = tile_map.sprite_lists["yard"]
        self.fence_list = tile_map.sprite_lists["fence"]
        self.stones_list = tile_map.sprite_lists["stones"]

        self.visible_lists = [
            self.castle_list,
            self.windows_list,
            self.yard_list,
            self.fence_list,
            self.stones_list,
            self.player_list,
            self.gems_list
        ]

        self.collisions_list = tile_map.sprite_lists["collisions"]

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.collisions_list
        )

        # Монетки
        for _ in range(random.randint(10, 15)):
            self.gems_list.append(arcade.Sprite(
                ':resources:images/items/gold_1.png', TILE_SCALING / 3,
                                                      70 * random.randint(1 + 1, 14 - 1),
                                                      70 * random.randint(1 + 1, 6 - 1)
            ))
        self.gems = len(self.gems_list)

        self.batch = Batch()

    def on_draw(self):
        """Отрисовка экрана"""
        self.clear()
        self.shaker.update_camera()
        self.world_camera.use()
        # Рисуем слои карты в правильном порядке
        for visible in self.visible_lists:
            visible.draw()
        self.shaker.readjust_camera()

        any_key_text = arcade.Text(f"Score: {self.gems - len(self.gems_list)}",
                                   0, self.window.height - 25,
                                   arcade.color.PURPLE, font_size=20, anchor_x="left", batch=self.batch)

        self.gui_camera.use()
        self.batch.draw()

    def on_update(self, delta_time: float):
        self.physics_engine.update()
        self.shaker.update(delta_time)

        for gem in arcade.check_for_collision_with_list(self.player, self.gems_list):
            gem.kill()
            self.shaker.start()

        cam_x, cam_y = self.world_camera.position
        dz_left = cam_x - DEAD_ZONE_W // 2
        dz_right = cam_x + DEAD_ZONE_W // 2
        dz_bottom = cam_y - DEAD_ZONE_H // 2
        dz_top = cam_y + DEAD_ZONE_H // 2

        px, py = self.player.center_x, self.player.center_y
        target_x, target_y = cam_x, cam_y

        if px < dz_left:
            target_x = px + DEAD_ZONE_W // 2
        elif px > dz_right:
            target_x = px - DEAD_ZONE_W // 2
        if py < dz_bottom:
            target_y = py + DEAD_ZONE_H // 2
        elif py > dz_top:
            target_y = py - DEAD_ZONE_H // 2

        # Не показываем «пустоту» за краями карты
        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        target_x = max(half_w, min(1050 - half_w, target_x))
        target_y = max(half_h, min(700 - half_h, target_y))

        # Плавно к цели, аналог arcade.math.lerp_2d, но руками
        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y
        self.cam_target = (smooth_x, smooth_y)

        self.world_camera.position = (self.cam_target[0], self.cam_target[1])

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.change_x = -SPEED
        if key == arcade.key.RIGHT:
            self.player.change_x = SPEED
        if key == arcade.key.DOWN:
            self.player.change_y = -SPEED
        if key == arcade.key.UP:
            self.player.change_y = SPEED

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.change_x = 0
        if key == arcade.key.RIGHT:
            self.player.change_x = 0
        if key == arcade.key.DOWN:
            self.player.change_y = 0
        if key == arcade.key.UP:
            self.player.change_y = 0


def main():
    """Главная функция"""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
