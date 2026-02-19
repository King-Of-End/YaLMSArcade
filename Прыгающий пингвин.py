import arcade
import random

from pyglet.graphics import Batch

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Пингвин и льдины"

# Разделение экрана на небо и воду
WATER_HEIGHT = SCREEN_HEIGHT // 3

# Физика прыжка
JUMP_HEIGHT = 15
GRAVITY = 0.8


class Floe(arcade.Sprite):
    """Класс льдины"""

    def __init__(self):
        super().__init__('images/floe.png', .2, random.randint(0, SCREEN_WIDTH), WATER_HEIGHT)
        self.speed = random.uniform(1, 3)
        self.direction = random.choice([-1, 1])  # 1 - вправо, -1 - влево
        self.change_x = self.speed * self.direction

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        """Обновление положения льдины"""
        if self.center_x < 0:
            self.center_x = 0
            self.change_x *= -1
        if self.center_x > SCREEN_WIDTH:
            self.center_x = SCREEN_WIDTH
            self.change_x *= -1


class GameWindow(arcade.Window):
    """Основной класс игры"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.batch = Batch()

    def setup(self):
        """Настройка игры"""
        self.all_sprites = arcade.SpriteList()
        self.floes = arcade.SpriteList()
        self.player = arcade.Sprite('images/penguin.png', .5, 10, self.center_y)
        self.all_sprites.append(self.player)
        for y in range(4):
            self.floes.append(Floe())
        self.floes[0].center_x = 0
        self.floes[0].change_x = 0
        self.floes[-1].center_x = SCREEN_WIDTH
        self.floes[-1].change_x = 0
        self.engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.floes,
            GRAVITY
        )
        self.game_over = False

    def on_draw(self):
        """Отрисовка игры"""
        self.clear()
        arcade.draw_rect_filled(arcade.LBWH(0, 0, SCREEN_WIDTH, WATER_HEIGHT), arcade.color.DARK_BLUE)
        arcade.draw_rect_filled(arcade.LBWH(0, WATER_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT), arcade.color.LIGHT_BLUE)
        self.floes.draw()
        self.all_sprites.draw()
        if self.game_over:
            text = arcade.text.Text(f'GAME OVER!',
                                    self.center_x * 0.4, self.center_y,
                                    arcade.color.RED_DEVIL, 40, batch=self.batch, bold=True, align='center')
        if self.game_over is None:
            text = arcade.text.Text(f'ПОБЕДА!',
                                    self.center_x * 0.4, self.center_y,
                                    arcade.color.RED_DEVIL, 40, batch=self.batch, bold=True, align='center')
        self.batch.draw()

    def on_update(self, delta_time):
        """Обновление игры"""
        if self.game_over in (True, None): return

        self.engine.update()
        self.floes.update()

        if self.player.center_y < WATER_HEIGHT:
            self.game_over = True

        if self.player.center_x > 0.9 * SCREEN_WIDTH:
            self.game_over = None

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.SPACE:
            self.engine.jump(JUMP_HEIGHT)
        if key == arcade.key.LEFT:
            self.player.change_x = -5
        if key == arcade.key.RIGHT:
            self.player.change_x = 5

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.LEFT:
            self.player.change_x = -0
        if key == arcade.key.RIGHT:
            self.player.change_x = 0


def setup_game(width=800, height=600, title="Пингвин и льдины"):
    game = GameWindow(width, height, title)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
