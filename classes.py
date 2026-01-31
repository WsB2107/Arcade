from config import *
import arcade



class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(scale=0.5)

        self.cur_texture = 0
        self.direction_view = 0

        # флаг атаки
        self.is_attacking = False

        # флаг супер способностей
        self.power = False

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
            texture = arcade.load_texture(f"textures/Warrior/Warrior_IDLE{i + 1}.png")
            self.idle_textures.append([texture, texture.flip_left_right()])

        # загрузка текстур для передвижения
        for i in range(6):
            texture = arcade.load_texture(f"textures/Warrior/Warrior_Run{i + 1}.png")
            self.run_textures.append([texture, texture.flip_left_right()])
        # загрузка текстур для атак
        for i in range(4):
            texture = arcade.load_texture(f"textures/Warrior/Warrior_Attack{i + 1}.png")
            self.attack_textures.append([texture, texture.flip_left_right()])

        # загрузка звук. эффектов получения урона
        self.hero_hit = arcade.load_sound("sound/hero_hit.mp3")

        jump_texture = arcade.load_texture("textures/Warrior/Warrior_Jump.png")
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

    def take_damage(self, count=1):
        if self.take_damage_timer <= 0:
            self.hp -= count
            self.take_damage_timer = 0.5
            arcade.play_sound(self.hero_hit, VOLUME["volume"])

            # индикатор получения урона
            self.color = arcade.color.RED

    def heal(self):

        # если хп игрока больше максимума, хп не восстановится
        if self.hp < self.max_hp:
            self.hp += 1
            if self.hp > self.max_hp:
                self.hp = self.max_hp


class Enemy(arcade.Sprite):
    def __init__(self, x, y, collision_list, platforms_list):
        super().__init__(scale=1)

        self.center_x = x
        self.center_y = y

        # текущая текстура и направление взгляда
        self.cur_texture = 0
        self.direction_view = 0

        # флаг атаки
        self.is_attacking = False

        # текстуры
        self.idle_textures = []
        self.run_textures = []
        self.attack_textures = []

        # IDLE

        texture = arcade.load_texture("textures/monsters/Skeleton/IDLE.png")
        self.idle_textures.append([texture, texture.flip_left_right()])

        # RUN
        for i in range(4):
            texture = arcade.load_texture(f"textures/monsters/Skeleton/walk{i + 1}.png")
            self.run_textures.append([texture, texture.flip_left_right()])

        #  ATTACK
        for i in range(8):
            texture = arcade.load_texture(f"textures/monsters/Skeleton/attack{i + 1}.png")
            self.attack_textures.append([texture, texture.flip_left_right()])

        # загрузка звук. эффектов
        self.skeleton_attack = arcade.load_sound("sound/skeleton_attack.wav")
        self.skeleton_hit = arcade.load_sound("sound/skeleton_hit.wav")
        self.skeleton_death = arcade.load_sound("sound/skeleton_death.wav")

        self.texture = self.idle_textures[0][0]

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

    def update_animation(self, delta_time: float = 1 / 60):
        if not self.idle_textures:
            return

        # красный цвет при получении урона
        if self.stun_timer > 0:
            self.color = arcade.color.RED
        else:
            self.color = arcade.color.WHITE

        # направление взгляда, если не атакует
        if not self.is_attacking:
            if self.change_x < -0.1:
                self.direction_view = 1
            elif self.change_x > 0.1:
                self.direction_view = 0

        # если игрок враг, то его сначала будет анимация атак
        if self.is_attacking and self.attack_textures:
            self.cur_texture += delta_time * 20
            frame = int(self.cur_texture)

            if frame < len(self.attack_textures):
                self.texture = self.attack_textures[frame][self.direction_view]
            else:

                # атака закончилась
                self.is_attacking = False
                self.cur_texture = 0
            return

        # передвижение
        if abs(self.change_x) > 0.1 and self.run_textures:
            self.cur_texture += delta_time * 10
            frame = int(self.cur_texture) % len(self.run_textures)
            self.texture = self.run_textures[frame][self.direction_view]
            return

        # idle
        self.texture = self.idle_textures[0][self.direction_view]

    def update_enemy(self, player, check):
        distance = arcade.get_distance_between_sprites(self, player)
        delta_time = 1 / 60

        # если враг оглушен, то он не преследует игрока
        if self.stun_timer > 0:
            self.stun_timer -= delta_time
            self.enemy_engine.update()
            return

        # если враг атакует, он стоит на месте
        if self.is_attacking:
            self.change_x = 0
            self.enemy_engine.update()
            return

        #  обновление таймера атаки
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

    def take_damage(self, direction, count=1):
        arcade.play_sound(self.skeleton_hit, volume=VOLUME["volume"])
        self.hp -= count

        # эффект оглушения
        self.stun_timer = 0.5

        # отбрасывание
        self.change_x = direction * 3
        self.change_y = 5

        if self.hp <= 0:
            self.remove_from_sprite_lists()
            arcade.play_sound(self.skeleton_death, volume=VOLUME["volume"])

    def attack_player(self, player, check):

        # враг атакует
        if not self.is_attacking:
            self.is_attacking = True
            self.cur_texture = 0
            self.change_x = 0
            arcade.play_sound(self.skeleton_attack, volume=1)

        if check:
            player.take_damage()

        # пауза между ударами
        self.attack_timer = 0.5


class Boss(arcade.Sprite):
    def __init__(self, x, y, collision_list, platforms_list):
        super().__init__(scale=2)

        self.center_x = x
        self.center_y = y

        # текущая текстура и направление взгляда
        self.cur_texture = 0
        self.direction_view = 0

        # флаг атаки
        self.is_attacking = False

        # текстуры
        self.idle_textures = []
        self.run_textures = []
        self.attack_textures = []

        # IDLE

        texture = arcade.load_texture("textures/monsters/boss/Boss_IDLE.png")
        self.idle_textures.append([texture, texture.flip_left_right()])

        # RUN
        for i in range(6):
            texture = arcade.load_texture(f"textures/monsters/boss/Boss_Run{i + 1}.png")
            self.run_textures.append([texture, texture.flip_left_right()])

        #  ATTACK
        for i in range(4):
            texture = arcade.load_texture(f"textures/monsters/boss/Boss_Attack{i + 1}.png")
            self.attack_textures.append([texture, texture.flip_left_right()])

        # загрузка звук. эффектов
        self.boss_attack = arcade.load_sound("sound/boss_attack.wav")
        self.boss_hit = arcade.load_sound("sound/boss_hit.wav")
        self.boss_death = arcade.load_sound("sound/boss_death.wav")
        self.end_boss_fight = arcade.load_sound("sound/end_boss_fight.mp3")
        self.end_boss = False

        self.texture = self.idle_textures[0][0]

        # движок для босса
        self.enemy_engine = arcade.PhysicsEnginePlatformer(
            self,
            walls=collision_list,
            platforms=platforms_list,
            gravity_constant=GRAVITY
        )

        # характеристики босса
        self.hp = 10
        self.speed_chase = ENEMY_MOVE_SPEED
        self.change_x = self.speed_chase

        # время до следующего удара
        self.attack_timer = 0

        # дистанция, при которой босс агрится
        self.dist_to_agr = 100000
        # дистанция удара
        self.attack_dist = 150

        # начальное состояние
        self.state = "преследование"

        # время оглушения
        self.stun_timer = 0

    def update_animation(self, delta_time: float = 1 / 60):
        if not self.idle_textures:
            return

        # красный цвет при получении урона
        if self.stun_timer > 0:
            self.color = arcade.color.RED
        else:
            self.color = arcade.color.WHITE

        # направление взгляда, если не атакует
        if not self.is_attacking:
            if self.change_x < -0.1:
                self.direction_view = 1
            elif self.change_x > 0.1:
                self.direction_view = 0

        # если атака, то его сначала будет анимация атак
        if self.is_attacking and self.attack_textures:
            self.cur_texture += delta_time *10
            frame = int(self.cur_texture)

            if frame < len(self.attack_textures):
                self.texture = self.attack_textures[frame][self.direction_view]
            else:

                # атака закончилась
                self.is_attacking = False
                self.cur_texture = 0
            return

        # передвижение
        if abs(self.change_x) > 0.1 and self.run_textures:
            self.cur_texture += delta_time * 8
            frame = int(self.cur_texture) % len(self.run_textures)
            self.texture = self.run_textures[frame][self.direction_view]
            return

        # idle
        self.texture = self.idle_textures[0][self.direction_view]

    def update_boss(self, player, check):
        distance = arcade.get_distance_between_sprites(self, player)
        delta_time = 1 / 60

        # если враг оглушен, то он не преследует игрока
        if self.stun_timer > 0:
            self.stun_timer -= delta_time
            self.enemy_engine.update()
            return

        # если враг атакует, он стоит на месте
        if self.is_attacking:
            self.change_x = 0
            self.enemy_engine.update()
            return

        #  обновление таймера атаки
        if self.attack_timer > 0:
            self.attack_timer -= delta_time

        # когда враг атакует
        if distance < self.attack_dist and self.attack_timer <= 0:
            self.attack_player(player, check)

        if self.state == "преследование":
            if distance > self.attack_dist - 10:
                if self.center_x < player.center_x:
                    self.change_x = self.speed_chase
                else:
                    self.change_x = -self.speed_chase
            else:

                #  если подошли очень близко
                self.change_x = 0

        self.enemy_engine.update()

    def take_damage(self, direction, count=1):
        arcade.play_sound(self.boss_hit, volume=VOLUME["volume"])
        self.hp -= count

        # эффект оглушения
        self.stun_timer = 0.1

        # малое отбрасывание
        self.change_x = direction
        self.change_y = 1

        if self.hp <= 0:
            arcade.play_sound(self.boss_death, volume=VOLUME["volume"] * 0.75)

            # победная музыка над боссом
            if not self.end_boss:
                arcade.play_sound(self.end_boss_fight, volume=VOLUME["volume"] * 0.5)
                self.end_boss = True

    def attack_player(self, player, check):

        # босс атакует
        if not self.is_attacking:
            self.is_attacking = True
            self.cur_texture = 0
            self.change_x = 0
            arcade.play_sound(self.boss_attack, volume=VOLUME["volume"])


        if check:
            player.take_damage(2)

        # пауза между ударами
        self.attack_timer = 0.5


# сердечки восстанавливают хп
class Heart(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("textures/heart.png", 1)
        self.center_x = x
        self.center_y = y
        self.health_up = arcade.load_sound("sound/health_up.wav")

    def update_heart(self, player, check):
        if check:
            player.heal()
            self.remove_from_sprite_lists()
            arcade.play_sound(self.health_up, volume=VOLUME["volume"])


# супер способность для босс файта
class SuperUp(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("textures/super.png", 2)
        self.center_x = x
        self.center_y = y
        self.hero_super = arcade.load_sound("sound/hero_super.wav")

    def update_super(self, player, check):
        if check:
            player.power = True
            self.remove_from_sprite_lists()
            arcade.play_sound(self.hero_super, volume=1)
