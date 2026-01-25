from config import *
from levels import *
import arcade


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

    def update_enemy(self, player):
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

