
from classes import *
from config import *
import arcade
from pyglet.graphics import Batch
from arcade import Camera2D


class TestView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLUE_YONDER)
        self.player = Player(480, 2800)
        self.enemies_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.player)

        self.tile_map = arcade.load_tilemap("level_1.tmx",
                                            scaling=1.0)  # Во встроенных ресурсах есть даже уровни!

        self.sky_list = self.tile_map.sprite_lists["sky"]
        self.grass_list = self.tile_map.sprite_lists["grass"]
        self.trees_list = self.tile_map.sprite_lists["trees"]
        self.backgr_list = self.tile_map.sprite_lists["backgr"]
        self.back2_list = self.tile_map.sprite_lists["back2"]
        self.back_list = self.tile_map.sprite_lists["back"]
        self.dekor1_list = self.tile_map.sprite_lists["dekor1"]
        self.dekor2_list = self.tile_map.sprite_lists["dekor2"]
        self.stone_list = self.tile_map.sprite_lists["stone"]
        self.stone_ground_list = self.tile_map.sprite_lists["stone_ground"]
        self.platforms_list = self.tile_map.sprite_lists["platforms"]
        self.dekor_list = self.tile_map.sprite_lists["dekor"]
        self.collision_list = self.tile_map.sprite_lists["collision"]
        for enemy_point in self.tile_map.object_lists.get("enemies", []):
            # Берем координаты из Tiled
            world_x = enemy_point.shape[0]
            world_y = enemy_point.shape[1]
            #print(world_x, world_y)

            # Создаем объект врага
            enemy = Enemy(world_x, world_y, self.collision_list, self.platforms_list)
            self.enemies_list.append(enemy)

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
            walls=self.collision_list,
            platforms=self.platforms_list,
            gravity_constant=GRAVITY
        )

    def on_draw(self):
        self.clear()
        self.world_camera.use()

        # 1. Сначала рисуем задние слои
        self.sky_list.draw()
        self.grass_list.draw()
        self.backgr_list.draw()
        self.back2_list.draw()
        self.back_list.draw()
        self.trees_list.draw()
        self.dekor1_list.draw()
        self.dekor2_list.draw()

        # 2. Рисуем основные слои
        self.stone_list.draw()
        self.stone_ground_list.draw()
        self.platforms_list.draw()
        self.collision_list.draw()

        # 4. РИСУЕМ ГЕРОЯ
        self.all_sprites.draw()

        self.enemies_list.draw()

        # декорации должны быть ПЕРЕД игроком
        self.dekor_list.draw()

        # GUI
        self.gui_caemra.use()
        self.batch.draw()

    def on_update(self, delta_time):
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

        self.all_sprites.update_animation(delta_time)
        self.enemies_list.update_animation(delta_time)

        world_w = 200000
        world_h = 200000
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_h, smooth[1]))

        self.world_camera.position = (cam_x, cam_y)
        self.gui_caemra.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        self.update_combat()
        self.enemies_list.update()  # Чтобы враги могли отлетать при ударе

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.up = True
        elif key == arcade.key.S:
            self.down = True
        elif key == arcade.key.A:
            self.left = True
        elif key == arcade.key.D:
            self.right = True
        if key == arcade.key.W:
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER
        if key == arcade.key.ESCAPE:
            self.window.close()
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        if key == arcade.key.SPACE:
            # Запускаем атаку, если она еще не идет
            if not self.player.is_attacking:
                self.player.is_attacking = True
                self.player.cur_texture = 0  # Сбрасываем счетчик, чтобы начать с 1 кадра
                self.player.already_hit = []  # Очищаем список при новом ударе

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.up = False
        elif key == arcade.key.S:
            self.down = False
        elif key == arcade.key.A:
            self.left = False
        elif key == arcade.key.D:
            self.right = False
        if key == arcade.key.W:
            self.jump_pressed = False
            self.jump_buffer_timer = JUMP_BUFFER

    def update_combat(self):
        # Проверяем атаку только на определенном кадре анимации (например, на 2-м или 3-м)
        # Это делает боевку "честной": урон наносится, когда меч визуально опускается
        frame = int(self.player.cur_texture)

        if self.player.is_attacking and frame in [2, 3]:
            # Создаем невидимый хитбокс атаки перед игроком
            # Смещаем его влево или вправо в зависимости от того, куда смотрит герой
            hitbox_dist = 50 if self.player.character_face_direction == 0 else -50

            # Ищем врагов, которые попали в зону удара
            hit_list = arcade.check_for_collision_with_list(self.player, self.enemies_list)

            # Если мы хотим более точный удар (чуть впереди игрока),
            # можно использовать get_sprites_at_point или создать временный спрайт-хитбокс

            for enemy in hit_list:
                if enemy not in self.player.already_hit:
                    enemy.hp -= 1
                    print(f"Враг получил урон! HP: {enemy.hp}")
                    self.player.already_hit.append(enemy)  # Помечаем врага как "получившего урон"

                    # Отбрасывание врага (Knockback)
                    if self.player.character_face_direction == 0:
                        enemy.change_x +=5
                    else:
                        enemy.change_x -= 5

                    if enemy.hp <= 0:
                        enemy.remove_from_sprite_lists()


