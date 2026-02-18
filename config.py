"""High-level configuration interface backed by SQLite."""

import sqlite3
from pathlib import Path

from db.manager import get_connection, get_setting, set_setting
from util.paths import DB_PATH


class Config:
    """OO wrapper around the settings database table.

    Args:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self._conn: sqlite3.Connection = get_connection(db_path)

    def get(self, key: str, default: str | None = None) -> str | None:
        """Return the value for *key*, or *default* if not found.

        Args:
            key: The setting key.
            default: Value to return when key is absent.

        Returns:
            The stored string value, or *default*.
        """
        value = get_setting(key, self._conn)
        return value if value is not None else default

    def set(self, key: str, value: str) -> None:
        """Persist *value* under *key* immediately.

        Args:
            key: The setting key.
            value: The string value to store.
        """
        set_setting(key, value, self._conn)

    def close(self) -> None:
        """Close the underlying database connection."""
        self._conn.close()
