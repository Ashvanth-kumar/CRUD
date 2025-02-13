import sqlite3

conn = sqlite3.connect('./DATABASE.db')
cur = conn.cursor()

cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
cur.execute('''
            CREATE TABLE IF NOT EXISTS sleep_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sleep_date DATE NOT NULL,
                sleep_start_time TIME NOT NULL,
                wakeup_time TIME NOT NULL,
                sleep_time REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

conn.commit()
conn.close()