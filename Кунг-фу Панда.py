import arcade
from arcade import check_for_collision_with_list
from pyglet.graphics import Batch

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Kung Fu Panda"
TILE_SCALING = 1.0


class GridGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Инициализируем списки спрайтов
        self.player_list = arcade.SpriteList()
        self.payer = arcade.Sprite(
            'assets/pandamini.png', TILE_SCALING / 2,
            self.center_x, self.center_y
        )
        self.player_list.append(self.payer)

        # ===== ВОЛШЕБСТВО ЗАГРУЗКИ КАРТЫ! (почти без магии) =====
        # Грузим тайловую карту
        tilemap = arcade.load_tilemap('assets/безымянный.tmx')

        # --- Достаём слои из карты как спрайт-листы ---
        self.wall_list = tilemap.sprite_lists['collision']
        self.bamboo_list = tilemap.sprite_lists['bamboo']
        self.exit_list = tilemap.sprite_lists['exit']
        self.ground_list = tilemap.sprite_lists['ground']

        # --- Физический движок. ---
        # Используем PhysicsEngineSimple, который знаем и любим
        # Он даст нам движение и коллизии со стенами (self.wall_list)!
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.payer,
            self.wall_list,
        )
        # Подсчёт съеденного бамбука
        self.score = 0
        self.end = False

        self.batch = Batch()

    def on_draw(self):
        """Отрисовка экрана"""
        self.clear()
        self.ground_list.draw()
        self.bamboo_list.draw()
        if len(self.bamboo_list) == 0:
            self.exit_list.visible = True
            if check_for_collision_with_list(self.payer, self.exit_list):
                self.end = True
                wintext = arcade.text.Text(f'ПОБЕДА',
                                self.center_x * 0.4, self.center_y,
                                arcade.color.RED_DEVIL, 100, batch=self.batch, bold=True, align='center')
        self.exit_list.draw()
        # Батч для текста
        self.player_list.draw()
        text = arcade.text.Text(f'Score: {self.score}',
                                0, self.height - 25,
                                arcade.color.RED_DEVIL, 20, batch=self.batch)

        self.batch.draw()

    def on_update(self, delta_time):
        """Обновление логики игры"""
        if self.end:
            return

        self.physics_engine.update()
        bamboo: arcade.Sprite
        for bamboo in arcade.check_for_collision_with_list(self.payer, self.bamboo_list):
            bamboo.kill()
            self.score += 1
        if (len(self.bamboo_list) == 0) == 1 and arcade.check_for_collision_with_list(self.payer, self.exit_list):
            self.end = True

    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш"""
        if key == arcade.key.UP:
            self.payer.change_y = 10
        if key == arcade.key.DOWN:
            self.payer.change_y = -10
        if key == arcade.key.LEFT:
            self.payer.change_x = -40
        if key == arcade.key.RIGHT:
            self.payer.change_x = 40

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.UP:
            self.payer.change_y = 0
        if key == arcade.key.DOWN:
            self.payer.change_y = -0
        if key == arcade.key.LEFT:
            self.payer.change_x = -0
        if key == arcade.key.RIGHT:
            self.payer.change_x = 0


def setup_game(width=960, height=640, title="Kung Fu Panda"):
    game = GridGame(width, height, title)
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()