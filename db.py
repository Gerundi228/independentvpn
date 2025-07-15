import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "vpn.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not DB_PATH.exists():
        conn = get_db()
        conn.executescript("""
        CREATE TABLE users (
          id         INTEGER PRIMARY KEY AUTOINCREMENT,
          tg_id      INTEGER UNIQUE,
          uuid       TEXT UNIQUE,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE regions (
          id     INTEGER PRIMARY KEY AUTOINCREMENT,
          code   TEXT UNIQUE,
          name   TEXT,
          domain TEXT,
          port   INTEGER DEFAULT 443,
          type   TEXT DEFAULT 'ws',
          path   TEXT DEFAULT '/vpn'
        );
        """)
        # Прелоадим три региона
        conn.executemany(
          "INSERT INTO regions (code,name,domain) VALUES (?,?,?)",
          [
            ("RU","Россия","ru.independentvpn.ru"),
            ("US","США",   "us.independentvpn.ru"),
            ("KZ","Казахстан","kz.independentvpn.ru"),
            ("FIN","Финляндия","fin.independentvpn.ru"),
          ]
        )
        conn.commit()
        conn.close()

def get_user(tg_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_user(tg_id, uuid):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO users (tg_id,uuid) VALUES (?,?)", (tg_id,uuid))
    conn.commit()
    conn.close()

def get_regions():
    conn = get_db()
    rows = conn.execute("SELECT * FROM regions ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]
