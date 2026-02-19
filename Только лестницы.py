import arcade

SCREEN_WIDTH = 768
SCREEN_HEIGHT = 450
SCREEN_TITLE = "Ladders Runner"
TILE_SCALING = 0.5
GRAVITY = 0.5
PLAYER_SPEED = 6
LADDER_SPEED = 3  # Скорость по лестнице


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.SPANISH_SKY_BLUE)

        self.player_list = arcade.SpriteList()
        self.player = arcade.Sprite(
            ':resources:/images/animated_characters/female_adventurer/femaleAdventurer_idle.png',
            TILE_SCALING, 32, 96
        )
        self.player_list.append(self.player)

        tilemap = arcade.load_tilemap('assets/ladders.tmx', TILE_SCALING)
        self.ground_list = tilemap.sprite_lists['ground']
        self.floor1_list = tilemap.sprite_lists['floor1']
        self.floor2_list = tilemap.sprite_lists['floor2']
        self.entry_exit_list = tilemap.sprite_lists['entry_exit']
        self.ladders_list = tilemap.sprite_lists['ladders']
        self.collision_list = tilemap.sprite_lists['collision']

        self.visible_lists = [
            self.ground_list,
            self.floor1_list,
            self.floor2_list,
            self.entry_exit_list,
            self.ladders_list,
            self.player_list,
        ]

        # Физический движок
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            ladders=self.ladders_list,
            walls=self.collision_list
        )

        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.jump_pressed = False
        self.time_since_ground = 0
        self.jumps_left = 1
        self.jump_buffer_timer = 0

    def on_draw(self):
        self.clear()
        for item in self.visible_lists:
            item.draw()

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
            self.jumps_left = 1
        else:
            self.time_since_ground += dt

        # Можно прыгать, если стоим на земле или в пределах койот-времени
        if self.jump_pressed and grounded:
                # Просим движок прыгнуть: он корректно задаст начальную вертикальную скорость
                self.physics_engine.jump(10)
                self.jump_buffer_timer = 0

        # Обновляем физику — движок сам двинет игрока и платформы
        self.physics_engine.update()


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


def setup_game(width=768, height=450, title="Ladders Runner"):
    game = MyGame(width, height, title)
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()