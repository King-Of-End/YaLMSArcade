import arcade
import random
import math

from pyglet.graphics import Batch

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Space Battle"
PLAYER_SCALING = 0.5
ITEM_SCALING = 0.05
ENEMY_SCALING = 0.1
PLAYER_MOVEMENT_SPEED = 5

class GridGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, antialiasing=True)

    def setup(self):
        self.bird_list = arcade.SpriteList()
        self.bird1 = arcade.Sprite(
            'images/plate.png', PLAYER_SCALING,
            self.center_x, 100
        )
        self.bird_list.append(self.bird1)

        self.fly_list = arcade.SpriteList()
        self.stone_list = arcade.SpriteList()

        self.batch = Batch()
        self.bird1.score = 0
        self.timer = 0
        self.timer1 = 0
        self.game_over = False
        self.texture = arcade.load_texture('images/stared_sky.png')

    def on_update(self, delta_time):
        """Обновление логики игры"""
        if self.game_over:
            return
        self.fly_list.update(delta_time)
        self.bird_list.update(delta_time)
        self.stone_list.update(delta_time)

        for fly in arcade.check_for_collision_with_list(self.bird1, self.fly_list):
            fly.kill()
            self.bird1.score += 1
        for fly in arcade.check_for_collision_with_list(self.bird1, self.stone_list):
            fly.kill()
            self.bird1.score -= 3

        if self.bird1.score < 0:
            self.game_over = True

        self.timer += delta_time * 2
        self.timer1 += delta_time * 2

        if self.timer1 > 1:
            speed = random.randint(5, 10)
            angle = random.uniform(math.pi / 3, math.pi * 2 / 3)
            change_y = math.cos(angle - 3 * math.pi / 2) * speed
            change_x = math.sin(angle - 3 * math.pi / 2) * speed
            star = arcade.Sprite(
                'images/star.png', ITEM_SCALING,
                random.randint(0, self.width), self.height,
            )
            star.velocity = (change_x, change_y)
            self.fly_list.append(star)
            self.timer1 -= 1
        if self.timer > 2:
            speed = random.randint(5, 10)
            angle = random.uniform(math.pi / 3, math.pi * 2 / 3)
            change_y = math.cos(angle - 3 * math.pi / 2) * speed
            change_x = math.sin(angle - 3 * math.pi / 2) * speed
            star = arcade.Sprite(
                'images/asteroid.png', ENEMY_SCALING,
                random.randint(0, self.width), self.height,
            )
            star.velocity = (change_x, change_y)
            self.stone_list.append(star)
            self.timer -= 2

    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш"""
        if key == arcade.key.UP:
            self.bird1.change_y = 20
        if key == arcade.key.DOWN:
            self.bird1.change_y = -20
        if key == arcade.key.LEFT:
            self.bird1.change_x = -20
        if key == arcade.key.RIGHT:
            self.bird1.change_x = 20


    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.LEFT:
            self.bird1.change_x = -0
        if key == arcade.key.RIGHT:
            self.bird1.change_x = 0


    def on_draw(self):
        self.clear()

        arcade.draw_texture_rect(self.texture, arcade.LBWH(
            0, 0, self.width, self.height))

        self.bird_list.draw()
        self.fly_list.draw()
        self.stone_list.draw()

        text1 = arcade.text.Text(f'Score: {self.bird1.score}',
                                0, 0,
                                arcade.color.RED_DEVIL, 20, batch=self.batch)
        if self.game_over:
            wintext = arcade.text.Text(f'GAME OVER!',
                                   self.center_x * 0.4, self.center_y,
                                   arcade.color.RED_DEVIL, 40, batch=self.batch, bold=True, align='center')
        self.batch.draw()


def setup_game(width=1024, height=640, title="Dolphins in the sea"):
    game = GridGame(width, height, title)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
