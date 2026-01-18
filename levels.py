from classes import *
from config import *
import arcade
from pyglet.graphics import Batch
from arcade import Camera2D

class TestView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLUE_YONDER)
        self.player = Player(100, 100)
        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.player)

        self.tile_map = arcade.load_tilemap(":resources:/tiled_maps/level_1.json",
                                            scaling=0.5)  # Во встроенных ресурсах есть даже уровни!
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.left = self.right = self.up = self.down = self.jump_pressed = False
        self.jump_buffer_timer = 0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS
        self.score = 0
        self.batch = Batch()
        self.world_camera = Camera2D()
        self.gui_caemra = Camera2D()

        # движок
        self.engine = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms=self.scene["Platforms"],
            gravity_constant=GRAVITY
        )

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.all_sprites.draw()
        self.scene.draw()
        self.gui_caemra.use()
        self.batch.draw()


    def on_update(self, delta_time):
        self.player.change_y -= GRAVITY
        move = 0
        if self.left and not self.right:
            move = -PLAYER_MOVE_SPEED
        elif self.right and not self.left:
            move = PLAYER_MOVE_SPEED
        self.player.change_x = move
        # Прыжок: can_jump() + койот + буфер
        grounded = self.engine.can_jump(y_distance=6)  # Есть пол под ногами?
        if grounded:
            self.time_since_ground = 0
            self.jumps_left = MAX_JUMPS
        else:
            self.time_since_ground += delta_time

        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= delta_time
        want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)

        if want_jump:
            can_coyote = (self.time_since_ground <= COYOTE_TIME)
            if grounded or can_coyote:
                # Просим движок прыгнуть: он корректно задаст начальную вертикальную скорость
                self.engine.jump(JUMP_SPEED)
                self.jump_buffer_timer = 0

        self.engine.update()
        target = (self.player.center_x, self.player.center_y)
        cx, cy = self.world_camera.position
        smooth = (cx + (target[0] - cx) * CAMERA_LERP,
                  cy + (target[1] - cy) * CAMERA_LERP)
        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2

        world_w = 2500
        world_h = 1100
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_h, smooth[1]))

        self.world_camera.position = (cam_x, cam_y)
        self.gui_caemra.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.up = True
        elif key == arcade.key.S:
            self.down = True
        elif key == arcade.key.A:
            self.left = True
        elif key == arcade.key.D:
            self.right = True
        elif key == arcade.key.SPACE:
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER
        if key == arcade.key.ESCAPE:
            self.window.close()
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.up = False
        elif key == arcade.key.S:
            self.down = False
        elif key == arcade.key.A:
            self.left = False
        elif key == arcade.key.D:
            self.right = False
        elif key == arcade.key.SPACE:
            self.jump_pressed = False
            self.jump_buffer_timer = JUMP_BUFFER


