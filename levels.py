from config import *
import arcade
from pyglet.graphics import Batch
from arcade import Camera2D


# Общий родительский класс для всех уровней
class GameLevel(arcade.View):
    def __init__(self, start_x, start_y, map_name, bg_color):
        super().__init__()
        arcade.set_background_color(bg_color)

        # игрок и спрайтлисты
        self.player = Player(start_x, start_y)
        self.enemies_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.player)

        self.tile_map = arcade.load_tilemap(map_name, scaling=1.0)

        # коллизия
        self.platforms_list = None
        self.collision_list = None
        self.ladder_list = None

        # статы игрока
        self.left = self.right = self.up = self.down = self.jump_pressed = False
        self.jump_buffer_timer = 0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS
        self.score = 0

        # камера
        self.batch = Batch()
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()  # Исправил опечатку caemra -> camera

        # движок
        self.engine = None

    def spawn_enemies(self):
        #  координаты врагов
        for enemy_point in self.tile_map.object_lists.get("enemies", []):
            world_x = enemy_point.shape[0]
            world_y = enemy_point.shape[1]
            enemy = Enemy(world_x, world_y, self.collision_list, self.platforms_list)
            self.enemies_list.append(enemy)

    def on_update(self, delta_time):
        # движение игрока
        move = 0
        if self.left and not self.right:
            move = -PLAYER_MOVE_SPEED
        elif self.right and not self.left:
            move = PLAYER_MOVE_SPEED
        self.player.change_x = move

        # проверка на лестницу
        if self.ladder_list and self.engine.is_on_ladder():
            if self.up:
                self.player.change_y = PLAYER_LADDER_SPEED
            elif self.down:
                self.player.change_y = -PLAYER_LADDER_SPEED
        else:
            # крутой прыжок
            grounded = self.engine.can_jump(y_distance=6)
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
                    self.engine.jump(JUMP_SPEED)
                    self.jump_buffer_timer = 0

        # движок
        self.engine.update()

        # обновление врагов и боевку
        for enemy in self.enemies_list:
            check = arcade.check_for_collision_with_list(self.player, self.enemies_list)
            enemy.update_enemy(self.player, check)

        self.update_combat()

        # уникальные ловушки для каждого уровня
        self.traps()

        # камера
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
        self.gui_camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        # экран смерти
        if self.player.hp <= 0:
            self.game_over()

    def traps(self):

        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.up = True
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER

        elif key == arcade.key.A:
            self.left = True

        elif key == arcade.key.D:
            self.right = True

        # чтобы падать быстрее
        elif key == arcade.key.S:
            self.down = True

        if key == arcade.key.ESCAPE:
            self.window.close()

        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)

        if key == arcade.key.SPACE:
            if not self.player.is_attacking:
                self.player.is_attacking = True

                # сбрасываем счетчик и список при каждом ударе
                self.player.cur_texture = 0
                self.player.already_hit = []

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.up = False
            self.jump_pressed = False
            self.jump_buffer_timer = JUMP_BUFFER
        elif key == arcade.key.S:
            self.down = False
        elif key == arcade.key.A:
            self.left = False
        elif key == arcade.key.D:
            self.right = False

    def update_combat(self):

        # считаем фреймы, чтобы вся анимация атаки не наносила урон
        frame = int(self.player.cur_texture)

        if self.player.is_attacking and frame in [2, 3]:
            hit_list = arcade.check_for_collision_with_list(self.player, self.enemies_list)

            # враги которым еще не нанесли урон
            for enemy in hit_list:
                if enemy not in self.player.already_hit:
                    # направление отбрасывания
                    direction = 1 if self.player.direction_view == 0 else -1

                    # нанесение урона
                    enemy.take_damage(direction)

                    # чтобы враг не получил больше 1 урона за тычку
                    self.player.already_hit.append(enemy)

    def game_over(self):
        game_view = self.__class__()
        self.window.show_view(game_view)


# уровень 1 - Шахты
class Mines(GameLevel):
    def __init__(self):
        # инициализация
        super().__init__(480, 2800, "level_1.tmx", arcade.color.BLUE_YONDER)

        # слои
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
        self.dekor_list = self.tile_map.sprite_lists["dekor"]

        # коллизия
        self.platforms_list = self.tile_map.sprite_lists["platforms"]
        self.collision_list = self.tile_map.sprite_lists["collision"]

        # враги
        self.spawn_enemies()

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

        # задние слои
        self.sky_list.draw()
        self.grass_list.draw()
        self.backgr_list.draw()
        self.back2_list.draw()
        self.back_list.draw()
        self.trees_list.draw()
        self.dekor1_list.draw()
        self.dekor2_list.draw()

        # основные слои
        self.stone_list.draw()
        self.stone_ground_list.draw()
        self.platforms_list.draw()
        self.collision_list.draw()

        # игрок и враги
        self.all_sprites.draw()
        self.enemies_list.draw()

        # декорации перед игроком
        self.dekor_list.draw()

        # GUI
        self.gui_camera.use()
        self.batch.draw()


# уровень 2 - Катакомбы
class Catacombs(GameLevel):
    def __init__(self):
        # инициализация
        super().__init__(128, 2800, "level_2.tmx", arcade.color.EERIE_BLACK)

        # слои
        self.backgr_list = self.tile_map.sprite_lists["backgr"]
        self.back2_list = self.tile_map.sprite_lists["back2"]
        self.back1_list = self.tile_map.sprite_lists["back1"]
        self.back_list = self.tile_map.sprite_lists["back"]
        self.spikes_list = self.tile_map.sprite_lists["spikes"]
        self.dekor2_list = self.tile_map.sprite_lists["dekor2"]
        self.dekor1_list = self.tile_map.sprite_lists["dekor1"]
        self.stone_list = self.tile_map.sprite_lists["stone"]
        self.collision_stone_list = self.tile_map.sprite_lists["collision_stone"]
        self.dekor_list = self.tile_map.sprite_lists["dekor"]

        # коллизия
        self.platforms_list = self.tile_map.sprite_lists["platforms"]
        self.collision_list = self.tile_map.sprite_lists["collision"]

        # враги
        self.spawn_enemies()

        # движок
        self.engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.collision_list,
            platforms=self.platforms_list,
            gravity_constant=GRAVITY
        )

    def traps(self):
        # шипы на уровне
        if arcade.check_for_collision_with_list(self.player, self.spikes_list):
            self.player.take_damage()

    def on_draw(self):
        self.clear()
        self.world_camera.use()

        # задние слои
        self.backgr_list.draw()
        self.back2_list.draw()
        self.back1_list.draw()
        self.back_list.draw()
        self.spikes_list.draw()
        self.dekor2_list.draw()
        self.dekor1_list.draw()

        # основные слои
        self.stone_list.draw()
        self.collision_stone_list.draw()
        self.platforms_list.draw()
        self.collision_list.draw()

        # враги и игрок
        self.all_sprites.draw()
        self.enemies_list.draw()

        # декор перед игроком
        self.dekor_list.draw()

        # GUI
        self.gui_camera.use()
        self.batch.draw()


# уровень 3 - Глубины
class Depths(GameLevel):
    def __init__(self):
        # инициализация
        super().__init__(128, 2570, "level_3.tmx", arcade.color.EERIE_BLACK)

        # слои
        self.backgr_list = self.tile_map.sprite_lists["backgr"]
        self.stone_collision_list = self.tile_map.sprite_lists["stone_collision"]
        self.stone_castle_list = self.tile_map.sprite_lists["stone_castle"]
        self.magma_list = self.tile_map.sprite_lists["magma"]
        self.stone_dungeon_list = self.tile_map.sprite_lists["stone_dungeon"]

        # коллизия и лестницы
        self.platforms_list = self.tile_map.sprite_lists["platforms"]
        self.ladder_list = self.tile_map.sprite_lists["ladder"]
        self.collision_list = self.tile_map.sprite_lists["collision"]

        # враги
        self.spawn_enemies()

        # движок
        self.engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.collision_list,
            platforms=self.platforms_list,
            gravity_constant=GRAVITY,
            ladders=self.ladder_list
        )

    def traps(self):
        # раскаленная магма
        if arcade.check_for_collision_with_list(self.player, self.magma_list):
            self.player.take_damage()

    def on_draw(self):
        self.clear()
        self.world_camera.use()

        # задние слои

        # основные слои
        self.backgr_list.draw()
        self.stone_collision_list.draw()
        self.stone_castle_list.draw()
        self.stone_dungeon_list.draw()
        self.ladder_list.draw()
        self.magma_list.draw()
        self.platforms_list.draw()
        self.collision_list.draw()

        # враги и игрок
        self.all_sprites.draw()
        self.enemies_list.draw()

        # GUI
        self.gui_camera.use()
        self.batch.draw()


class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(scale=0.5)

        self.cur_texture = 0
        self.direction_view = 0

        # флаг атаки
        self.is_attacking = False

        # списки текстур
        self.idle_textures = []
        self.run_textures = []
        self.attack_textures = []
        self.jump_texture = []

        # список врагов, которых мы уже ударили за текущую атаку
        self.already_hit = []

        # хп игрока
        self.hp = 5
        self.max_hp = 5

        # таймер неуязвимости после получения урона
        self.take_damage_timer = 0

        # загрузка IDLE
        for i in range(8):
            texture = arcade.load_texture(f"textures/Warrior_IDLE{i + 1}.png")
            self.idle_textures.append([texture, texture.flip_left_right()])

        # загрузка текстур для передвижения
        for i in range(6):
            texture = arcade.load_texture(f"textures/Warrior_Run{i + 1}.png")
            self.run_textures.append([texture, texture.flip_left_right()])
        # загрузка текстур для атак
        for i in range(4):
            texture = arcade.load_texture(f"textures/Warrior_Attack{i + 1}.png")
            self.attack_textures.append([texture, texture.flip_left_right()])

        jump_texture = arcade.load_texture("textures/Warrior_Jump.png")
        self.jump_texture = [jump_texture, jump_texture.flip_left_right()]

        self.texture = self.idle_textures[0][0]
        self.center_x = x
        self.center_y = y

    def update_animation(self, delta_time: float = 1 / 60):

        # обратно в привычный цвет
        if self.take_damage_timer > 0:
            self.take_damage_timer -= delta_time
        else:
            self.color = arcade.color.WHITE

        if not self.is_attacking:

            # если игрок идет налево
            if self.change_x < -0.1:
                self.direction_view = 1
            # если игрок идет направо
            elif self.change_x > 0.1:
                self.direction_view = 0

        # если игрок атакует, то его сначало будет анимация атаки
        if self.is_attacking:
            self.cur_texture += delta_time * 10
            frame = int(self.cur_texture)

            if frame < 4:
                self.texture = self.attack_textures[frame][self.direction_view]
            else:

                # атака закончилась
                self.is_attacking = False
                self.cur_texture = 0
            return

        # когда игрок прыгает, он закрывается щитом, чтоб не получать урон от падения
        if abs(self.change_y) > 0.5:
            # подбираем нужную текстуру
            self.texture = self.jump_texture[self.direction_view]
            return

        # если игрок двигается, анимация бега
        if abs(self.change_x) > 0.1:
            # подбираем нужную текстуру
            self.cur_texture += delta_time * 10
            frame = int(self.cur_texture) % 6
            self.texture = self.run_textures[frame][self.direction_view]
            return

        # анимация покоя
        self.cur_texture += delta_time * 10
        frame = int(self.cur_texture) % 8
        self.texture = self.idle_textures[frame][self.direction_view]

    def take_damage(self):
        if self.take_damage_timer <= 0:
            self.hp -= 1
            self.take_damage_timer = 0.5

            # индикатор получения урона
            self.color = arcade.color.RED
            print(f"получил урон, осталось{self.hp}")

    def heal(self):

        # если хп игрока больше максимума, хп не восстановится
        if self.hp < self.max_hp:
            self.hp += 1
            if self.hp > self.max_hp:
                self.hp = self.max_hp
            print(f"Жизнь восстановлена! HP: {self.hp}")
            return True  # Возвращаем True, если лечение прошло успешно
        return False  # Возвращаем False, если здоровье и так полное


class Enemy(arcade.Sprite):
    def __init__(self, x, y, collision_list, platforms_list):
        super().__init__("textures/test.jpg", 1)
        self.center_x = x
        self.center_y = y

        # точка куда враг возвращается
        self.start_x = x
        self.patrol_range = 150

        # движок для врагов
        self.enemy_engine = arcade.PhysicsEnginePlatformer(
            self,
            walls=collision_list,
            platforms=platforms_list,
            gravity_constant=GRAVITY
        )

        # характеристики врага
        self.hp = 3
        self.speed_patrol = ENEMY_MOVE_SPEED
        self.speed_chase = ENEMY_MOVE_SPEED * 2
        self.change_x = self.speed_patrol

        # время до следующего удара
        self.attack_timer = 0

        # дистанция, при которой враг агрится
        self.dist_to_agr = 350
        # дистанция удара
        self.attack_dist = 60

        # начальное состояние
        self.state = "патруль"

        # время оглушения
        self.stun_timer = 0

    def update_enemy(self, player, check):
        distance = arcade.get_distance_between_sprites(self, player)
        delta_time = 1 / 60

        # если враг оглушен, то он не преследует игрока
        if self.stun_timer > 0:
            self.stun_timer -= delta_time
            self.enemy_engine.update()
            return

        # обновление таймера атаки
        if self.attack_timer > 0:
            self.attack_timer -= delta_time

        # когда враг атакует
        if distance < self.attack_dist and self.attack_timer <= 0:
            self.attack_player(player, check)

        # преследование игрока
        elif distance < self.dist_to_agr:
            self.state = "преследование"

        else:

            # игрок убежал далеко, возвращаемся к патрулю
            if self.state == "преследование":
                self.state = "патруль"

                # направление в сторону начальной точки
                self.change_x = self.speed_patrol if self.center_x < self.start_x else -self.speed_patrol

        # переключение состояний
        if self.state == "преследование":
            if distance > self.attack_dist - 10:
                if self.center_x < player.center_x:
                    self.change_x = self.speed_chase
                else:
                    self.change_x = -self.speed_chase
            else:

                #  если подошли очень близко
                self.change_x = 0

        elif self.state == "патруль":

            # разворот при выходе за границы радиуса
            if self.center_x > self.start_x + self.patrol_range:
                self.change_x = -self.speed_patrol
            elif self.center_x < self.start_x - self.patrol_range:
                self.change_x = self.speed_patrol

            # если уперся в стену раньше времени
            if abs(self.change_x) < 0.1:
                self.change_x = self.speed_patrol if self.center_x < self.start_x else -self.speed_patrol

        self.enemy_engine.update()

    def take_damage(self, direction):
        self.hp -= 1

        # эффект оглушения
        self.stun_timer = 0.5

        # отбрасывание
        self.change_x = direction * 3
        self.change_y = 5

        if self.hp <= 0:
            self.remove_from_sprite_lists()

    def attack_player(self, player, check):
        if check:
            player.take_damage()

        # пауза между ударами
        self.attack_timer = 2.0


class Heart(arcade.Sprite):
    def __init__(self, x, y, collision_list, platforms_list):
        super().__init__("textures/heart.jpg", 2)
        self.center_x = x
        self.center_y = y
