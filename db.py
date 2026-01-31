import sqlite3


class Database:
    def __init__(self, database="database.db"):

        self.database = database
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()

    def user_exists(self, username):  # проверка существования пользователя

        self.cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone() is not None

    def register_user(self, username, password):  # регистрация

        self.cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()
        return True

    def login_user(self, username, password):  # вход

        self.cursor.execute("SELECT id, username FROM users WHERE username = ? AND password = ?",
                            (username, password))
        user = self.cursor.fetchone()
        return user

    def get_all_users(self):

        self.cursor.execute("SELECT id, username FROM users ORDER BY username")
        return self.cursor.fetchall()

    def get_user_id(self, username):  # возвращает ид юзера

        self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return result[0]

    def save_level_progress(self, user_id, level_num, time_seconds):  # сохранение прогресса

        self.cursor.execute("""INSERT OR REPLACE INTO level_progress (user_id, level_num, time_seconds) 
                VALUES (?, ?, ?)""", (user_id, level_num, time_seconds))
        self.conn.commit()
        return True

    def get_level_progress(self, user_id, level_num):  # получение прогресса

        self.cursor.execute("SELECT * FROM level_progress WHERE user_id = ? AND level_num = ?",
                            (user_id, level_num))
        return self.cursor.fetchone()

    def save_record(self, user_id, level_num, best_time):  # сохранение рекорда
        print(f"[БАЗА ДАННЫХ] Сохранение рекорда: user_id={user_id}, level={level_num}, time={best_time}")

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
        return True

    def get_user_record(self, user_id, level_num):  # получение рекорда конкретного пользователя
        self.cursor.execute("SELECT * FROM records WHERE user_id = ? AND level_num = ?",
                            (user_id, level_num))
        return self.cursor.fetchone()

    def get_top_records_for_level(self, level_num, limit=10):  # отдельный метод для лидерборда

        self.cursor.execute("""SELECT r.user_id, u.username, r.best_time FROM records r
                              JOIN users u ON r.user_id = u.id WHERE r.level_num = ?
                              ORDER BY r.best_time ASC LIMIT ?""",
                            (level_num, limit))
        return self.cursor.fetchall()

    def unlock_level(self, user_id, level_num):

        self.cursor.execute("INSERT OR IGNORE INTO unlocked_levels (user_id, level_num) VALUES (?, ?)",
                            (user_id, level_num))
        self.conn.commit()
        return True

    def is_level_unlocked(self, user_id, level_num):

        self.cursor.execute("SELECT 1 FROM unlocked_levels WHERE user_id = ? AND level_num = ?",
                            (user_id, level_num))
        return self.cursor.fetchone() is not None

    def get_unlocked_levels(self, user_id):

        self.cursor.execute("SELECT level_num FROM unlocked_levels WHERE user_id = ? ORDER BY level_num",
                            (user_id,))
        result = self.cursor.fetchall()
        return [level[0] for level in result]

    def unlock_next_level(self, user_id, completed_level):  # после прохождения уровня вызывается

        next_level = completed_level + 1
        if next_level <= 4:
            return self.unlock_level(user_id, next_level)
        return False

    def close(self):

        self.conn.close()
