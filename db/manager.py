"""SQLite3 database layer for DashApp state persistence."""

import sqlite3
from pathlib import Path

from util.paths import DB_PATH


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open (or create) the database file and ensure schema exists.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        An open sqlite3 connection with row_factory set.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create required tables if they do not already exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.commit()


def get_setting(key: str, conn: sqlite3.Connection) -> str | None:
    """Retrieve a setting value by key.

    Args:
        key: The setting key to look up.
        conn: An open database connection.

    Returns:
        The stored value, or None if the key does not exist.
    """
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_setting(key: str, value: str, conn: sqlite3.Connection) -> None:
    """Upsert a setting value.

    Args:
        key: The setting key.
        value: The value to store.
        conn: An open database connection.
    """
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()
