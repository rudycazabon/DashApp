"""Tests for loader — plugin discovery and validation."""

import json
from pathlib import Path
from unittest.mock import patch

from loader import _read_manifest, load_tools


def test_empty_tools_dir_returns_empty(tmp_path: Path) -> None:
    """load_tools on an empty directory returns an empty list."""
    with patch("loader.TOOLS_DIR", tmp_path):
        result = load_tools()
    assert result == []


def test_demo_tool_discovered() -> None:
    """The demo tool is discovered and loaded from the real tools directory."""
    tools = load_tools()
    names = [t.name for t in tools]
    assert "Demo" in names


def test_missing_manifest_skipped(tmp_path: Path) -> None:
    """A tool directory with no manifest.json is silently skipped."""
    tool_dir = tmp_path / "notool"
    tool_dir.mkdir()
    (tool_dir / "tool.py").write_text("class Tool: pass")
    with patch("loader.TOOLS_DIR", tmp_path):
        result = load_tools()
    assert result == []


def test_missing_tool_py_skipped(tmp_path: Path) -> None:
    """A tool directory with no tool.py is silently skipped."""
    tool_dir = tmp_path / "broken"
    tool_dir.mkdir()
    (tool_dir / "manifest.json").write_text(
        json.dumps({"name": "Broken", "version": "0.1.0"})
    )
    with patch("loader.TOOLS_DIR", tmp_path):
        result = load_tools()
    assert result == []


def test_read_manifest_valid(tmp_path: Path) -> None:
    """_read_manifest returns a dict when JSON is valid and has 'name'."""
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps({"name": "Test", "version": "1.0"}))
    result = _read_manifest(p)
    assert result is not None
    assert result["name"] == "Test"


def test_read_manifest_missing_name(tmp_path: Path) -> None:
    """_read_manifest returns None when the 'name' key is absent."""
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps({"version": "1.0"}))
    assert _read_manifest(p) is None


def test_read_manifest_bad_json(tmp_path: Path) -> None:
    """_read_manifest returns None when JSON is malformed."""
    p = tmp_path / "manifest.json"
    p.write_text("{not valid json}")
    assert _read_manifest(p) is None
