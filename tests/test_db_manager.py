"""Tests for db.manager — schema creation, get/set, upsert."""

import sqlite3
from pathlib import Path

from db.manager import get_connection, get_setting, set_setting


def test_schema_created(tmp_path: Path) -> None:
    """Schema must exist after get_connection returns."""
    db = tmp_path / "test.db"
    conn = get_connection(db)
    # settings table should exist
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='settings'"
    ).fetchone()
    assert row is not None
    conn.close()


def test_get_missing_key_returns_none(tmp_path: Path) -> None:
    """get_setting on an absent key returns None."""
    conn = get_connection(tmp_path / "test.db")
    assert get_setting("missing", conn) is None
    conn.close()


def test_set_and_get_roundtrip(tmp_path: Path) -> None:
    """A value stored with set_setting is retrievable with get_setting."""
    conn = get_connection(tmp_path / "test.db")
    set_setting("theme", "dark", conn)
    assert get_setting("theme", conn) == "dark"
    conn.close()


def test_set_setting_upserts(tmp_path: Path) -> None:
    """set_setting overwrites an existing value without raising."""
    conn = get_connection(tmp_path / "test.db")
    set_setting("theme", "dark", conn)
    set_setting("theme", "light", conn)
    assert get_setting("theme", conn) == "light"
    conn.close()


def test_parent_dir_created(tmp_path: Path) -> None:
    """get_connection creates parent directories automatically."""
    db = tmp_path / "nested" / "dir" / "test.db"
    conn = get_connection(db)
    assert db.exists()
    conn.close()


def test_row_factory_set(tmp_path: Path) -> None:
    """Connection uses sqlite3.Row as row_factory."""
    conn = get_connection(tmp_path / "test.db")
    assert conn.row_factory is sqlite3.Row
    conn.close()
