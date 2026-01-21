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
