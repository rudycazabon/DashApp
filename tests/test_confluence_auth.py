"""Tests for tools/confluence/auth.py — Basic Auth session management."""

from pathlib import Path
from unittest.mock import patch

import pytest

from tools.confluence.auth import CREDENTIALS_PATH, get_auth
from util.paths import APP_DIR


def test_credentials_path_under_app_dir() -> None:
    """CREDENTIALS_PATH is confluence_credentials.json inside APP_DIR (~/.dashapp/)."""
    assert CREDENTIALS_PATH.name == "confluence_credentials.json"
    assert CREDENTIALS_PATH.parent == APP_DIR


def test_get_auth_raises_when_credentials_file_missing(tmp_path: Path) -> None:
    """FileNotFoundError is raised when confluence_credentials.json is absent."""
    missing = tmp_path / "confluence_credentials.json"
    with patch("tools.confluence.auth.CREDENTIALS_PATH", missing):
        with pytest.raises(
            FileNotFoundError, match="confluence_credentials.json not found"
        ):
            get_auth()


def test_get_auth_raises_when_keys_missing(tmp_path: Path) -> None:
    """ValueError is raised when required keys are missing."""
    creds_path = tmp_path / "confluence_credentials.json"
    creds_path.write_text('{"url": "https://example.atlassian.net"}')
    with patch("tools.confluence.auth.CREDENTIALS_PATH", creds_path):
        with pytest.raises(ValueError, match="missing required keys"):
            get_auth()


def test_get_auth_returns_session_with_basic_auth(tmp_path: Path) -> None:
    """get_auth configures Basic Auth from the credentials file."""
    creds_path = tmp_path / "confluence_credentials.json"
    creds_path.write_text(
        '{"url": "https://example.atlassian.net", '
        '"email": "user@example.com", "api_token": "token123"}'
    )
    with patch("tools.confluence.auth.CREDENTIALS_PATH", creds_path):
        session, _ = get_auth()

    assert session.auth == ("user@example.com", "token123")
    assert session.headers["Accept"] == "application/json"


def test_get_auth_returns_correct_base_url(tmp_path: Path) -> None:
    """get_auth returns the site root URL (no /wiki suffix added here)."""
    creds_path = tmp_path / "confluence_credentials.json"
    creds_path.write_text(
        '{"url": "https://example.atlassian.net", "email": "u@e.com", "api_token": "t"}'
    )
    with patch("tools.confluence.auth.CREDENTIALS_PATH", creds_path):
        _, base_url = get_auth()

    assert base_url == "https://example.atlassian.net"


def test_get_auth_strips_trailing_slash_from_url(tmp_path: Path) -> None:
    """get_auth strips a trailing slash from the URL."""
    creds_path = tmp_path / "confluence_credentials.json"
    creds_path.write_text(
        '{"url": "https://example.atlassian.net/", '
        '"email": "u@e.com", "api_token": "t"}'
    )
    with patch("tools.confluence.auth.CREDENTIALS_PATH", creds_path):
        _, base_url = get_auth()

    assert base_url == "https://example.atlassian.net"
