import sqlite3


class Database:
    def __init__(self, database="database.db"):
        self.database = database
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()

    def register_user(self, username, password):  # регистрация
        self.cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()

    def login_user(self, username, password):  # вход
        self.cursor.execute("SELECT id, username FROM users WHERE username = ? AND password = ?",
                            (username, password))
        user = self.cursor.fetchone()
        return user

    def get_user_id(self, username):  # возвращает ид юзера
        self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return result[0]

    def save_level_progress(self, user_id, level_num, time_seconds):  # сохранение прогресса
        self.cursor.execute("""INSERT OR REPLACE INTO level_progress (user_id, level_num, time_seconds) 
                VALUES (?, ?, ?)""", (user_id, level_num, time_seconds))
        self.conn.commit()

    def get_level_progress(self, user_id, level_num):  # получение прогресса
        self.cursor.execute("SELECT * FROM level_progress WHERE user_id = ? AND level_num = ?",
                            (user_id, level_num))
        return self.cursor.fetchone()

    def save_record(self, user_id, level_num, best_time):  # сохранение рекорда
        self.cursor.execute("SELECT best_time FROM records WHERE user_id = ? AND level_num = ?",
                            (user_id, level_num))
        existing = self.cursor.fetchone()
        if existing:
            if best_time < existing[0]:
                self.cursor.execute("""UPDATE records SET best_time = ? WHERE user_id = ? AND level_num = ?""",
                                    (best_time, user_id, level_num))
        else:
            self.cursor.execute("""INSERT INTO records (user_id, level_num, best_time) VALUES (?, ?, ?)""",
                                (user_id, level_num, best_time))
        self.conn.commit()

    def get_user_record(self, user_id, level_num):  # получение рекорда
        self.cursor.execute("SELECT * FROM records WHERE user_id = ? AND level_num = ?",
                            (user_id, level_num))
        return self.cursor.fetchone()
