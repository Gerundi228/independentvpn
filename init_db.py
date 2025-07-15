#!/usr/bin/env python3
import sqlite3

DB = 'vpn.db'
conn = sqlite3.connect(DB)
conn.executescript("""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS regions (
  id     INTEGER PRIMARY KEY AUTOINCREMENT,
  code   TEXT UNIQUE NOT NULL,
  name   TEXT NOT NULL,
  domain TEXT UNIQUE NOT NULL,
  port   INTEGER NOT NULL DEFAULT 443,
  type   TEXT NOT NULL    DEFAULT 'ws',
  path   TEXT NOT NULL    DEFAULT '/vpn'
);

CREATE TABLE IF NOT EXISTS users (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  tg_id      INTEGER UNIQUE NOT NULL,
  uuid       TEXT    UNIQUE NOT NULL,
  created_at DATETIME           DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO regions(code,name,domain) VALUES
  ('RU','Россия','ru.independentvpn.ru'),
  ('US','США','us.independentvpn.ru'),
  ('KZ','Казахстан','kz.independentvpn.ru'),
  ('FIN','Финляндия','fin.independentvpn.ru');
""")
conn.commit()
conn.close()
print("vpn.db создан и заполнен начальными регионами.")
