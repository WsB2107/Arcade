from db import Database


class User:
    def __init__(self):

        self.db = Database()
        self.current_user = None
        self.is_logged_in = False
        self.username = None
        self.user_id = None

    def register(self, username, password):

        if not username or not password:
            return False, "Имя пользователя и пароль не могут быть пустыми"

        if self.db.user_exists(username):
            return False, "Пользователь с таким именем уже существует"

        success = self.db.register_user(username, password)

        if success:
            return self.login(username, password)
        return success

    def login(self, username, password):

        if not username or not password:
            return False, "Введите имя пользователя и пароль"

        user = self.db.login_user(username, password)

        if user:
            self.current_user = user
            self.is_logged_in = True
            self.username = user[1]
            self.user_id = user[0]
            return True, f'Добро пожаловать, {self.username}'
        else:
            return False, "Неверное имя пользователя или пароль"

    def logout(self):

        self.current_user = None
        self.is_logged_in = False
        self.username = None
        self.user_id = None

    def save_level_progress(self, level_num, time_seconds):

        progress_success = self.db.save_level_progress(self.user_id, level_num, time_seconds)
        record_success = self.db.save_record(self.user_id, level_num, time_seconds)
        return progress_success and record_success

    def get_level_progress(self, level_num):

        progress = self.db.get_level_progress(self.user_id, level_num)

        if progress:
            return {'level_num': progress[2], 'completed': bool(progress[3]), 'time_seconds': progress[3]}
        return None

    def get_user_record(self, level_num):

        record = self.db.get_user_record(self.user_id, level_num)

        if record:
            return {'level_num': record[2], 'best_time': record[3]}
        return None

    def get_unlocked_levels(self):

        progress_list = self.db.get_all_levels_progress(self.user_id)
        unlocked = 1

        for progress in progress_list:
            level_num = progress[2]
            time_seconds = progress[3]

            if time_seconds > 0:
                unlocked = max(unlocked, level_num + 1)

        return unlocked
