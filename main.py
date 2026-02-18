import arcade

SCREEN_WIDTH = 1050
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Castle Tiles"
TILE_SCALING = 1.0
SPEED = 4

class Payer(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(
            '',
            TILE_SCALING,
            x, y
        )


class GridGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.player = arcade.Sprite(
            ':resources:images/animated_characters/robot/robot_idle.png', TILE_SCALING,
            self.center_x, self.center_y / 2
        )

        # Инициализируем списки спрайтов
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

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
        ]

        self.collisions_list = tile_map.sprite_lists["collisions"]

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.collisions_list
        )

    def on_draw(self):
        """Отрисовка экрана."""
        self.clear()

        # Рисуем слои карты в правильном порядке
        for visible in self.visible_lists:
            visible.draw()

    def on_update(self, delta_time: float):
        self.physics_engine.update()

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


def setup_game(width=1050, height=700, title="Castle Tiles"):
    game = GridGame(width, height, title)
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()