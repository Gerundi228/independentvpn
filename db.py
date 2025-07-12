import sqlite3
from datetime import datetime, timedelta

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
      user_id   INTEGER PRIMARY KEY,
      uuid      TEXT    NOT NULL,
      region    TEXT    NOT NULL,
      expires   DATE    NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def add_user_record(user_id: int, uuid_str: str, region: str, days: int = 30):
    expires = (datetime.now() + timedelta(days=days)).date().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "REPLACE INTO users (user_id, uuid, region, expires) VALUES (?,?,?,?)",
        (user_id, uuid_str, region, expires)
    )
    conn.commit()
    conn.close()

def get_user_record(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT uuid, region, expires FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row  # None или (uuid, region, expires)
