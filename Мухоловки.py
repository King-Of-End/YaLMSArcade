import arcade
import random
import math

from pyglet.graphics import Batch

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Fly Hunt"
BIRD_SPEED = 4
FLY_SPEED = 2
FLY_COUNT = 10
FLY_CHANGE_DIRECTION_CHANCE = 0.02


class Fly(arcade.Sprite):
    def __init__(self, x, y, scale=0.1):
        super().__init__('images/fly.png', scale, x, y)
        self.set_random_direction()

    def set_random_direction(self):
        """ Set a random movement direction for the fly """
        angle = random.uniform(0, 2 * math.pi)
        self.change_x = math.cos(angle) * FLY_SPEED
        self.change_y = math.sin(angle) * FLY_SPEED

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        """ Move the fly and randomly change direction occasionally """
        super().update(delta_time, *args, **kwargs)
        # Random direction change
        if random.random() < FLY_CHANGE_DIRECTION_CHANCE:
            self.set_random_direction()
        if self.center_x < 0 or self.center_x > SCREEN_WIDTH:
            self.change_x *= -1
        if self.center_y < 0 or self.center_y > SCREEN_HEIGHT:
            self.change_y *= -1

class GridGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, antialiasing=True)
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self):
        self.bird_list = arcade.SpriteList()
        self.bird1 = arcade.Sprite(
            'images/bird1.png', 0.2,
            self.center_x * 0.25, self.center_y
        )
        self.bird2 = arcade.Sprite(
            'images/bird2.png', 0.2,
            self.center_x * 0.75, self.center_y
        )
        self.bird_list.append(self.bird1)
        self.bird_list.append(self.bird2)

        self.fly_list = arcade.SpriteList()
        for _ in range(FLY_COUNT):
            self.fly_list.append(Fly(random.randint(0, SCREEN_WIDTH),
                                     random.randint(0, SCREEN_HEIGHT)))

        self.batch = Batch()
        self.bird1.score = 0
        self.bird2.score = 0

    def on_update(self, delta_time):
        """Обновление логики игры"""
        self.fly_list.update()
        self.bird_list.update()

        for fly in arcade.check_for_collision_with_list(self.bird1, self.fly_list):
            fly.kill()
            self.bird1.score += 1
        for fly in arcade.check_for_collision_with_list(self.bird2, self.fly_list):
            fly.kill()
            self.bird2.score += 1


    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш"""
        if key == arcade.key.UP:
            self.bird1.change_y = 20
        if key == arcade.key.DOWN:
            self.bird1.change_y = -20
        if key == arcade.key.LEFT:
            self.bird1.texture = arcade.load_texture('images/bird1.png').flip_horizontally()
            self.bird1.change_x = -20
        if key == arcade.key.RIGHT:
            self.bird1.texture = arcade.load_texture('images/bird1.png')
            self.bird1.change_x = 20

        if key == arcade.key.W:
            self.bird2.change_y = 20
        if key == arcade.key.S:
            self.bird2.change_y = -20
        if key == arcade.key.A:
            self.bird2.texture = arcade.load_texture('images/bird2.png')
            self.bird2.change_x = -20
        if key == arcade.key.D:
            self.bird2.texture = arcade.load_texture('images/bird2.png').flip_horizontally()
            self.bird2.change_x = 20

        if key == arcade.key.SPACE:
            if len(self.fly_list) == 0:
                self.setup()

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.UP:
            self.bird1.change_y = 0
        if key == arcade.key.DOWN:
            self.bird1.change_y = -0
        if key == arcade.key.LEFT:
            self.bird1.change_x = -0
        if key == arcade.key.RIGHT:
            self.bird1.change_x = 0

        if key == arcade.key.W:
            self.bird2.change_y = 0
        if key == arcade.key.S:
            self.bird2.change_y = -0
        if key == arcade.key.A:
            self.bird2.change_x = -0
        if key == arcade.key.D:
            self.bird2.change_x = 0

    def on_draw(self):
        self.clear()

        self.bird_list.draw()
        self.fly_list.draw()

        text1 = arcade.text.Text(f'Score of bird 1: {self.bird1.score}',
                                0, 0,
                                arcade.color.RED_DEVIL, 20, batch=self.batch)
        text2 = arcade.text.Text(f'Score of bird 2: {self.bird2.score}',
                                self.width - 220, 0,
                                arcade.color.RED_DEVIL, 20, batch=self.batch)
        if len(self.fly_list) == 0:
            wintext = arcade.text.Text(f'ПОБЕДА, нажмите пробел что ещё играть',
                                   self.center_x * 0.4, self.center_y,
                                   arcade.color.RED_DEVIL, 20, batch=self.batch, bold=True, align='center')

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
