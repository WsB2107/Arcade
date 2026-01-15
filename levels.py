import arcade

class TestView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLUE_YONDER)
        self.player_texture = arcade.load_texture("textures/test.jpg")
        self.player = arcade.Sprite(self.player_texture, 0.5)
        self.player.center_x = self.width // 2
        self.player.center_y = self.height // 2
        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.player)

        self.tile_map = arcade.load_tilemap(":resources:/tiled_maps/level_2.json",
                                            scaling=0.5)  # Во встроенных ресурсах есть даже уровни!
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Физический движок
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.scene["Platforms"])

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self.all_sprites.draw()

    def on_update(self, delta_time):
        # Обновляем физику
        self.physics_engine.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.change_y = 2
        elif key == arcade.key.DOWN:
            self.player.change_y = -2
        elif key == arcade.key.LEFT:
            self.player.change_x = -2
        elif key == arcade.key.RIGHT:
            self.player.change_x = 2

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.UP, arcade.key.DOWN]:
            self.player.change_y = 0
        if key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.player.change_x = 0


