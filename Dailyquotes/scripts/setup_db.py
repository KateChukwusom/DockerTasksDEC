import sqlite3

DB_PATH = "scripts/storage.db"

connection = sqlite3.connect(DB_PATH)
cur = connection.cursor()

# USERS
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'active',
    frequency TEXT DEFAULT 'daily'
)
""")

# QUOTES
cur.execute("""
CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote TEXT NOT NULL,
    author TEXT NOT NULL,
    date_fetched TEXT UNIQUE
)
""")

# EMAIL LOGS
cur.execute("""
CREATE TABLE IF NOT EXISTS email_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    sent_date TEXT NOT NULL,
    status TEXT,
    UNIQUE(email, sent_date)
)
""")


cur.executemany("""
INSERT OR IGNORE INTO users (name, email, status, frequency)
VALUES (?, ?, ?, ?)
""", [
    ("Chisom", "chisomokeke823@gmail.com", "active", "daily"),
    ("Kate", "okekekatesom@gmail.com", "inactive", "daily"),
    ("Raphael", "patraffiah@gmail.com", "active", "daily"),
    ("Victor", "mrmailerg2i@gmail.com", "active", "daily")
])

connection.commit()
connection.close()

print("Database initialized safely")
