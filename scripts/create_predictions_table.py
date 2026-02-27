#!/usr/bin/env python3
"""Create the predictions table in the SQLite database."""
import sqlite3
import os

DB_PATH = os.environ.get("DB_FILE", "data.db")

conn = sqlite3.connect(DB_PATH)
conn.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id INTEGER NOT NULL,
        driver_id INTEGER NOT NULL,
        constructor_id INTEGER,
        grid INTEGER,
        predicted_position INTEGER NOT NULL,
        actual_position INTEGER,
        predicted_delta INTEGER,
        actual_delta INTEGER,
        confidence REAL,
        model_version TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (race_id) REFERENCES races(id),
        FOREIGN KEY (driver_id) REFERENCES drivers(id)
    );
""")
conn.commit()
conn.close()
print("predictions table created successfully")
