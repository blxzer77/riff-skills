import os
import sqlite3


def path() -> str:
    return os.environ.get("PANTRY_DB", "/data/pantry.db")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(path())
    conn.row_factory = sqlite3.Row
    return conn
