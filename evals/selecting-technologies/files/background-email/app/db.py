import os

import psycopg


class Database:
    def __init__(self, url: str | None = None):
        self._conn = psycopg.connect(url or os.environ["DATABASE_URL"], autocommit=True)

    def insert_user(self, email: str, name: str) -> int:
        row = self._conn.execute(
            "INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", (email, name)
        ).fetchone()
        return row[0]
