import arcade
import random

from pyglet.graphics import Batch

# ---------- Окно и мир ----------
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Dolphins in the sea"
TILE_SCALING = 1.0

# ---------- Камера ----------
CAMERA_LERP = 0.12


class GridGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, antialiasing=True)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Камеры: мир и GUI
        self.world_camera = arcade.Camera2D()  # Камера для игрового мира
        self.gui_camera = arcade.Camera2D()  # Камера для объектов интерфейса

        # Данные уровня
        self.tile_map = None

        # Слои с нашими спрайтами
        self.player_list = arcade.SpriteList()
        self.player = arcade.Sprite()

        # Игрок
        self.player = None

        # Батч для текста
        self.batch = Batch()
        self.text_info = arcade.Text(
            "WASD/стрелки — движение",
            20, 20, arcade.color.BLACK, 14, batch=self.batch
        )

        self.tile_map = arcade.load_tilemap('assets/see.tmx')
        self.sea_list = self.tile_map.sprite_lists['sea']
        self.wall_list = self.tile_map.sprite_lists['collision']

        # Уточняем размеры мира по карте
        self.world_height = self.tile_map.height
        self.world_width = self.tile_map.width

        self.player_textures = [
            arcade.load_texture('assets/dolphin.png'),
            arcade.load_texture('assets/dolphin.png').flip_horizontally(),
        ]

        # Создаём игроков
        self.player = arcade.Sprite(self.player_textures[0], 0.25,
                                    1500, 1000)
        self.player1 = arcade.Sprite(self.player_textures[0], 0.25,
                                    self.world_height // 2 - 100, self.world_width // 2 - 100,)
        self.player2 = arcade.Sprite(self.player_textures[0], 0.25,
                                    self.world_height // 2 + 100, self.world_width // 2 - 100,)
        self.player_list.append(self.player)
        self.player_list.append(self.player1)
        self.player_list.append(self.player2)
        # Физический движок
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.wall_list,
        )

    def on_update(self, delta_time):
        """Обновление логики игры"""
        print(self.player.position)
        self.physics_engine.update()
        if self.player.center_y > 1810.5 - 100:
            self.player.center_y = 1810.5 - 100
        if self.player.center_y < 109.5 + 100:
            self.player.center_y = 109.5 + 100
        if self.player.center_x < 118.0 + 100:
            self.player.center_x = 118.0 + 100
        self.world_camera.position = (self.player.center_x, self.player.center_y)
        self.player1.position = (self.player.center_x - 100, self.player.center_y - 100)
        self.player2.position = (self.player.center_x - 100, self.player.center_y + 100)

    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш"""
        if key == arcade.key.UP:
            self.player.change_y = 20
        if key == arcade.key.DOWN:
            self.player.change_y = -20
        if key == arcade.key.LEFT:
            for player in self.player_list:
                player.texture = self.player_textures[1]
            self.player.change_x = -20
        if key == arcade.key.RIGHT:
            for player in self.player_list:
                player.texture = self.player_textures[0]
            self.player.change_x = 20

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.UP:
            self.player.change_y = 0
        if key == arcade.key.DOWN:
            self.player.change_y = -0
        if key == arcade.key.LEFT:
            self.player.change_x = -0
        if key == arcade.key.RIGHT:
            self.player.change_x = 0

    def on_draw(self):
        self.clear()

        # 1) Мир.
        self.world_camera.use()
        self.sea_list.draw()
        # 2) GUI.
        self.player_list.draw()

        self.gui_camera.use()
        self.batch.draw()


def setup_game(width=1024, height=640, title="Dolphins in the sea"):
    game = GridGame(width, height, title)
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
