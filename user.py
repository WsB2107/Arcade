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
