import sqlite3
import json
from contextlib import closing


class DB:

    @staticmethod
    def query(db_name, query_get, query_post=()):
        with closing(sqlite3.connect(db_name)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    if query_post:
                        cursor.execute(query_get, query_post)
                    else:
                        cursor.execute(query_get)
                    return cursor.fetchall()

    def __init__(self, app):
        self.query('settings.db',
                   'CREATE TABLE IF NOT EXISTS init_settings (id INT PRIMARY KEY, shared_key VARCHAR(16))')
        self.query('settings.db',
                   'CREATE TABLE IF NOT EXISTS bot_settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, set_num VARCHAR(16), set_desc TEXT)')
        self.query('settings.db',
                   'CREATE TABLE IF NOT EXISTS alarm_settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, exchange TEXT, pair TEXT, alarm_desc TEXT)')

        self.query('position.db',
                   'CREATE TABLE IF NOT EXISTS position_settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, exchange TEXT, pair TEXT, price REAL, qty REAL)')
        self.query('position.db',
                   'CREATE TABLE IF NOT EXISTS strategy_settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, exchange TEXT, pair TEXT, strategy_desc TEXT)')

        row = self.query('settings.db', 'SELECT * FROM init_settings')
        if not row:
            self.query('settings.db', 'INSERT INTO init_settings (id, shared_key) VALUES (1, "demo")')
        self.app = app

    def save_key(self, shared_key):
        if self.app.user.activation.check():
            self.query('settings.db', 'UPDATE init_settings SET shared_key=? WHERE id=?', (shared_key, 1))
            return 0

    def load_key(self):
        row = self.query('settings.db', 'SELECT * FROM init_settings')
        return row[0][1]

    def get_settings_list(self):
        if self.app.user.activation.check():
            row = self.query('settings.db', 'SELECT * FROM bot_settings')
            return sorted([row[i][1] for i in range(len(row))]) if row != [] else list()

    def del_bot_settings(self, num):
        if self.app.user.activation.check():
            self.query('settings.db', 'DELETE FROM bot_settings WHERE set_num = ?', (num,))
            return 0

    def save_bot_settings(self, num, data):
        if self.app.user.activation.check():
            data_json = json.dumps(data)
            row = self.query('settings.db', 'SELECT * FROM bot_settings WHERE set_num=?', (num,))
            if row:
                self.query('settings.db', 'UPDATE bot_settings SET set_desc=? WHERE set_num=?', (data_json, num))
            else:
                self.query('settings.db', 'INSERT INTO bot_settings (id, set_num, set_desc) VALUES (null, ?, ?)', (num, data_json))
            return 0

    def load_bot_settings(self, num):
        if self.app.user.activation.check():
            row = self.query('settings.db', 'SELECT * FROM bot_settings WHERE set_num = ?', (num,))
            return json.loads(row[0][2]) if row != [] else dict()

    def save_position(self, exchange, pair, price, qty):
        if self.app.user.activation.check():
            row = self.query('position.db', 'SELECT * FROM position_settings WHERE exchange=? AND pair=?', (exchange, pair))
            if row:
                self.query('position.db', 'UPDATE position_settings SET price=?, qty=? WHERE exchange=? AND pair=?',
                           (price, qty, exchange, pair))
            else:
                self.query('position.db',
                           'INSERT INTO position_settings (id, exchange, pair, price, qty) VALUES (null, ?, ?, ?, ?)',
                           (exchange, pair, 0.0, 0.0))
            return 0

    def load_position(self, exchange, pair):
        if self.app.user.activation.check():
            row = self.query('position.db', 'SELECT * FROM position_settings WHERE exchange=? AND pair=?', (exchange, pair))
            return (row[0][3], row[0][4]) if row != [] else (0.0, 0.0)

    def save_strategy(self, exchange, pair, data):
        if self.app.user.activation.check():
            data_json = json.dumps(data)
            row = self.query('position.db',
                             'SELECT * FROM strategy_settings WHERE exchange=? AND pair=?',
                             (exchange, pair))
            if row:
                self.query('position.db',
                           'UPDATE strategy_settings SET strategy_desc=? WHERE exchange=? AND pair=?',
                           (data_json, exchange, pair))
            else:
                self.query('position.db',
                           'INSERT INTO strategy_settings (id, exchange, pair, strategy_desc) VALUES (null, ?, ?, ?)',
                           (exchange, pair, data_json))
            return 0

    def load_strategy(self, exchange, pair):
        if self.app.user.activation.check():
            row = self.query('position.db', 'SELECT * FROM strategy_settings WHERE exchange=? AND pair=?', (exchange, pair))
            return json.loads(row[0][3]) if row != [] else dict()

    def save_alarm(self, exchange, pair, data):
        if self.app.user.activation.check():
            data_json = json.dumps(data)
            row = self.query('settings.db',
                             'SELECT * FROM alarm_settings WHERE exchange=? AND pair=?',
                             (exchange, pair))
            if row:
                self.query('settings.db',
                           'UPDATE alarm_settings SET alarm_desc=? WHERE exchange=? AND pair=?',
                           (data_json, exchange, pair))
            else:
                self.query('settings.db',
                           'INSERT INTO alarm_settings (id, exchange, pair, alarm_desc) VALUES (null, ?, ?, ?)',
                           (exchange, pair, data_json))
            return 0

    def load_alarm(self, exchange, pair):
        if self.app.user.activation.check():
            row = self.query('settings.db', 'SELECT * FROM alarm_settings WHERE exchange=? AND pair=?', (exchange, pair))
            return json.loads(row[0][3]) if row != [] else dict()
