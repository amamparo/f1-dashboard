import sqlite3

import bcrypt

AVATAR_BASE_URL = "https://api.dicebear.com/9.x/identicon/svg"


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def init_users_table(conn: sqlite3.Connection):
    """Create the users table and seed default users if they don't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            avatar TEXT NOT NULL DEFAULT '',
            role TEXT NOT NULL DEFAULT 'member',
            must_change_password INTEGER NOT NULL DEFAULT 1,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.commit()

    # Migration: add role column if missing (for existing DBs)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "role" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'member'")
        conn.execute("UPDATE users SET role = 'admin' WHERE username IN ('janedoe', 'johndoe')")
        conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        users = [
            (
                "janedoe",
                "Jane Doe",
                _hash_password("password"),
                f"{AVATAR_BASE_URL}?seed=janedoe",
                "admin",
                0,
            ),
            (
                "johndoe",
                "John Doe",
                _hash_password("password"),
                f"{AVATAR_BASE_URL}?seed=johndoe",
                "admin",
                0,
            ),
        ]
        conn.executemany(
            "INSERT INTO users"
            " (username, full_name, hashed_password, avatar, role, must_change_password)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            users,
        )
        conn.commit()
