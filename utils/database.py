import sqlite3
import traceback

class Connection:
    def __enter__(self):
        self.conn = sqlite3.connect("data.db")
        self.create_table()
        return self

    def create_table(self):
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS user_voice(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                engine TEXT NOT NULL,
                voice TEXT NOT NULL
                );"""
        )

    def set_user_voice(self, user, engine, voice):
        if not self.get_user_voice(user):
            self.conn.execute(f"INSERT INTO user_voice VALUES (NULL, '{user}', '{engine}', '{voice}')")
        else:
            self.conn.execute(f"UPDATE user_voice SET voice = '{voice}', engine = '{engine}' WHERE user = '{user}'")
        self.conn.commit()

    def get_user_voice(self, user):
        cursor = self.conn.execute(f"SELECT engine, voice FROM user_voice WHERE user = '{user}'")
        data = cursor.fetchone()
        if not data:
            return None
        return data

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_traceback:
            traceback.print_exc()
        self.conn.close()
