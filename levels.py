from classes import *
from config import *
import arcade
from pyglet.graphics import Batch
from arcade import Camera2D


class Mines(arcade.View):
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
            # print(world_x, world_y)

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

        for enemy in self.enemies_list:
            enemy.update_enemy(self.player)
        self.update_combat()
        # self.enemies_list.update()

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
        for enemy in self.enemies_list:
            enemy.update_enemy(self.player)
        self.update_combat()
        self.enemies_list.update()  # Чтобы враги могли отлетать при ударе
        if self.player.hp <= 0:
            self.game_over()

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
            # hitbox_dist = 50 if self.player.character_face_direction == 0 else -50

            # Ищем врагов, которые попали в зону удара
            hit_list = arcade.check_for_collision_with_list(self.player, self.enemies_list)

            # Если мы хотим более точный удар (чуть впереди игрока),
            # можно использовать get_sprites_at_point или создать временный спрайт-хитбокс

            for enemy in hit_list:
                if enemy not in self.player.already_hit:
                    # Определяем направление отбрасывания
                    direction = 1 if self.player.character_face_direction == 0 else -1

                    # Наносим урон и передаем направление
                    enemy.take_damage(1, direction)

                    self.player.already_hit.append(enemy)

    def game_over(self):
        print("Игра окончена!")
        # Здесь можно перезапустить уровень или вернуть в меню
        game_view = Mines()  # Перезапуск
        self.window.show_view(game_view)


class Catacombs(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.EERIE_BLACK)
        self.player = Player(128, 2800)
        self.enemies_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.player)

        self.tile_map = arcade.load_tilemap("level_2.tmx",
                                            scaling=1.0)  # Во встроенных ресурсах есть даже уровни!

        self.backgr_list = self.tile_map.sprite_lists["backgr"]
        self.back2_list = self.tile_map.sprite_lists["back2"]
        self.back1_list = self.tile_map.sprite_lists["back1"]
        self.back_list = self.tile_map.sprite_lists["back"]
        self.dekor2_list = self.tile_map.sprite_lists["dekor2"]
        self.dekor1_list = self.tile_map.sprite_lists["dekor1"]
        self.stone_list = self.tile_map.sprite_lists["stone"]
        self.collision_stone_list = self.tile_map.sprite_lists["collision_stone"]
        self.platforms_list = self.tile_map.sprite_lists["platforms"]
        self.dekor_list = self.tile_map.sprite_lists["dekor"]
        self.collision_list = self.tile_map.sprite_lists["collision"]

        for enemy_point in self.tile_map.object_lists.get("enemies", []):
            # Берем координаты из Tiled
            world_x = enemy_point.shape[0]
            world_y = enemy_point.shape[1]
            # print(world_x, world_y)

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
        self.backgr_list.draw()
        self.back2_list.draw()
        self.back1_list.draw()
        self.back_list.draw()
        self.dekor2_list.draw()
        self.dekor1_list.draw()

        # 2. Рисуем основные слои
        self.stone_list.draw()
        self.collision_stone_list.draw()
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

        for enemy in self.enemies_list:
            enemy.update_enemy(self.player)
        self.update_combat()
        # self.enemies_list.update()

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
        for enemy in self.enemies_list:
            enemy.update_enemy(self.player)
        self.update_combat()
        self.enemies_list.update()  # Чтобы враги могли отлетать при ударе
        if self.player.hp <= 0:
            self.game_over()

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
            # hitbox_dist = 50 if self.player.character_face_direction == 0 else -50

            # Ищем врагов, которые попали в зону удара
            hit_list = arcade.check_for_collision_with_list(self.player, self.enemies_list)

            # Если мы хотим более точный удар (чуть впереди игрока),
            # можно использовать get_sprites_at_point или создать временный спрайт-хитбокс

            for enemy in hit_list:
                if enemy not in self.player.already_hit:
                    # Определяем направление отбрасывания
                    direction = 1 if self.player.character_face_direction == 0 else -1

                    # Наносим урон и передаем направление
                    enemy.take_damage(1, direction)

                    self.player.already_hit.append(enemy)

    def game_over(self):
        print("Игра окончена!")
        # Здесь можно перезапустить уровень или вернуть в меню
        game_view = Catacombs()  # Перезапуск
        self.window.show_view(game_view)


class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(scale=0.5)

        self.cur_texture = 0
        self.character_face_direction = 0
        self.is_attacking = False  # Флаг атаки

        # Списки текстур
        self.idle_textures = []
        self.run_textures = []
        self.attack_textures = []
        self.jump_texture_pair = []  # Для прыжка

        self.already_hit = []  # Список врагов, которых мы уже ударили за текущую атаку
        self.hp = 5
        self.invulnerability_timer = 0  # Таймер неуязвимости после удара

        # Загрузка IDLE (8 кадров)
        for i in range(8):
            texture = arcade.load_texture(f"textures/Warrior_IDLE{i + 1}.png")
            self.idle_textures.append([texture, texture.flip_left_right()])

        # Загрузка RUN (6 кадров)
        for i in range(6):
            texture = arcade.load_texture(f"textures/Warrior_Run{i + 1}.png")
            self.run_textures.append([texture, texture.flip_left_right()])
            # Загрузка ATTACK (4 кадра)
        for i in range(4):
            texture = arcade.load_texture(f"textures/Warrior_Attack{i + 1}.png")
            self.attack_textures.append([texture, texture.flip_left_right()])

        jump_tex = arcade.load_texture("textures/Warrior_Jump.png")
        self.jump_texture_pair = [jump_tex, jump_tex.flip_left_right()]

        self.texture = self.idle_textures[0][0]
        self.center_x = x
        self.center_y = y

    def update_animation(self, delta_time: float = 1 / 60):
        # 1. Направление взгляда (не меняем во время атаки, если хотим зафиксировать удар)
        if not self.is_attacking:
            if self.change_x < -0.1:
                self.character_face_direction = 1
            elif self.change_x > 0.1:
                self.character_face_direction = 0

        # 2. Логика АТАКИ (Самый высокий приоритет)
        if self.is_attacking:
            self.cur_texture += delta_time * 12  # Скорость удара
            frame = int(self.cur_texture)

            if frame < 4:
                self.texture = self.attack_textures[frame][self.character_face_direction]
            else:
                # Атака закончилась
                self.is_attacking = False
                self.cur_texture = 0
            return  # Выходим, чтобы другие анимации не мешали

        # 3. Анимация прыжка
        if abs(self.change_y) > 0.5:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return

        # 4. Анимация бега
        if abs(self.change_x) > 0.1:
            self.cur_texture += delta_time * 12
            frame = int(self.cur_texture) % 6
            self.texture = self.run_textures[frame][self.character_face_direction]
            return

        # 5. Анимация покоя
        self.cur_texture += delta_time * 10
        frame = int(self.cur_texture) % 8
        self.texture = self.idle_textures[frame][self.character_face_direction]

        if self.invulnerability_timer > 0:
            self.invulnerability_timer -= delta_time
        else:
            self.color = arcade.color.WHITE

    def take_damage(self, amount):
        if self.invulnerability_timer <= 0:
            self.hp -= amount
            self.invulnerability_timer = 0.3  # 1.5 секунды неуязвимости
            self.color = arcade.color.RED_DEVIL  # Игрок краснеет
            print(f"Игрок получил урон! HP: {self.hp}")


class Enemy(arcade.Sprite):
    def __init__(self, x, y, collision_list, platforms_list):
        super().__init__("textures/test.jpg", 1)
        self.center_x = x
        self.center_y = y

        # Запоминаем начальную точку для патруля
        self.start_x = x
        self.patrol_range = 150  # Радиус патрулирования (вправо и влево)

        self.enemy_engine = arcade.PhysicsEnginePlatformer(
            self,
            walls=collision_list,
            platforms=platforms_list,
            gravity_constant=GRAVITY
        )

        self.hp = 3
        self.speed_patrol = 1  # Скорость при патруле
        self.speed_chase = 2  # Скорость при погоне
        self.dist_to_agressive = 350

        self.change_x = self.speed_patrol
        self.state = "PATROL"  # Текущее состояние
        self.stun_timer = 0

        self.attack_dist = 60  # Дистанция удара
        self.attack_cooldown = 2.0  # Пауза между ударами (секунды)
        self.attack_timer = 0  # Текущее время до следующего удара

    def update_enemy(self, player):
        # Уменьшаем таймер атаки
        if self.attack_timer > 0:
            self.attack_timer -= 1 / 60

        # Если враг оглушен — логику не выполняем
        if self.stun_timer > 0:
            self.stun_timer -= 1 / 60
            self.enemy_engine.update()
            return

        distance = arcade.get_distance_between_sprites(self, player)

        # ЛОГИКА АТАКИ
        if distance < self.attack_dist and self.attack_timer <= 0:
            self.attack_player(player)

        # ЛОГИКА ПРЕСЛЕДОВАНИЯ (только если не стоим вплотную)
        elif distance < self.dist_to_agressive:
            if distance > self.attack_dist - 10:  # Чтобы не "дрожал" в упор
                if self.center_x < player.center_x:
                    self.change_x = self.speed_chase
                else:
                    self.change_x = -self.speed_chase
            else:
                self.change_x = 0  # Останавливаемся, если подошли очень близко

        # Если враг оглушен, он только ждет и подчиняется физике (отлетает)
        if self.stun_timer > 0:
            self.stun_timer -= 1 / 60  # Уменьшаем таймер (при 60 FPS)
            self.enemy_engine.update()
            return  # Выходим из метода, чтобы логика CHASE не сработала

        distance = arcade.get_distance_between_sprites(self, player)

        # 1. ПЕРЕКЛЮЧЕНИЕ СОСТОЯНИЙ
        if distance < self.dist_to_agressive:
            self.state = "CHASE"
        else:
            # Если игрок убежал далеко, возвращаемся к патрулю
            if self.state == "CHASE":
                self.state = "PATROL"
                # Выбираем направление в сторону дома, чтобы не застрять
                self.change_x = self.speed_patrol if self.center_x < self.start_x else -self.speed_patrol

        # 2. ВЫПОЛНЕНИЕ ЛОГИКИ
        if self.state == "CHASE":
            # Логика погони
            if self.center_x < player.center_x:
                self.change_x = self.speed_chase
            else:
                self.change_x = -self.speed_chase

        elif self.state == "PATROL":
            # Логика патрулирования: разворот при выходе за границы радиуса
            if self.center_x > self.start_x + self.patrol_range:
                self.change_x = -self.speed_patrol
            elif self.center_x < self.start_x - self.patrol_range:
                self.change_x = self.speed_patrol

            # Дополнительная проверка: если уперся в стену раньше времени
            if abs(self.change_x) < 0.1:
                self.change_x = self.speed_patrol if self.center_x < self.start_x else -self.speed_patrol

        # 3. ПРИМЕНЕНИЕ ФИЗИКИ
        self.enemy_engine.update()

    def take_damage(self, amount, knockback_dir):
        self.hp -= amount

        # Включаем оглушение на 0.5 секунды
        self.stun_timer = 0.5

        # Сильное отбрасывание (dir — это 1 или -1)
        self.change_x = knockback_dir * 3
        self.change_y = 5  # Подбросим его чуть-чуть вверх для эффекта

        if self.hp <= 0:
            self.remove_from_sprite_lists()

    def attack_player(self, player):
        print("Враг атакует!")
        player.take_damage(1)
        self.attack_timer = self.attack_cooldown
