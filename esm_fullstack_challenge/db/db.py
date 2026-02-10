import sqlite3
from contextlib import contextmanager


class DB:
    """Database class for managing SQLite connections."""
    def __init__(self, db_file: str):
        self.db_file = db_file

    @contextmanager
    def get_connection(self):
        """Context manager for database connection."""
        conn = sqlite3.connect("data.db")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
