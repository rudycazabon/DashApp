"""Tests for Config — the high-level settings interface."""

from pathlib import Path

from config import Config


def test_missing_key_returns_none(tmp_path: Path) -> None:
    """get on an absent key with no default returns None."""
    cfg = Config(tmp_path / "test.db")
    assert cfg.get("nonexistent") is None
    cfg.close()


def test_missing_key_with_default(tmp_path: Path) -> None:
    """get on an absent key returns the provided default."""
    cfg = Config(tmp_path / "test.db")
    assert cfg.get("nonexistent", "fallback") == "fallback"
    cfg.close()


def test_set_and_get_roundtrip(tmp_path: Path) -> None:
    """A value stored with set is returned by get."""
    cfg = Config(tmp_path / "test.db")
    cfg.set("lang", "en")
    assert cfg.get("lang") == "en"
    cfg.close()


def test_overwrite(tmp_path: Path) -> None:
    """set overwrites a previously stored value."""
    cfg = Config(tmp_path / "test.db")
    cfg.set("color", "blue")
    cfg.set("color", "red")
    assert cfg.get("color") == "red"
    cfg.close()


def test_persistence_across_instances(tmp_path: Path) -> None:
    """Values written by one Config instance are readable by another."""
    db = tmp_path / "test.db"
    cfg1 = Config(db)
    cfg1.set("persistent", "yes")
    cfg1.close()

    cfg2 = Config(db)
    assert cfg2.get("persistent") == "yes"
    cfg2.close()
