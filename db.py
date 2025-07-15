# db.py
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
        conn.executemany(
          "INSERT INTO regions (code,name,domain) VALUES (?,?,?)",
          [
            ("RU","Россия","ru.independentvpn.ru"),
            ("US","США","us.independentvpn.ru"),
            ("KZ","Казахстан","kz.independentvpn.ru"),
            ("FIN","Финляндия","fin.independentvpn.ru"),
          ]
        )
        conn.commit()
        conn.close()

def get_regions():
    conn = get_db()
    rows = conn.execute("SELECT * FROM regions ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]
