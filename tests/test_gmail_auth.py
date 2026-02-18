"""Tests for tools/gmail/auth.py — OAuth credential management."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tools.gmail.auth import CREDENTIALS_PATH, TOKEN_PATH, get_credentials
from util.paths import APP_DIR


def test_credentials_path_points_to_project_root() -> None:
    """CREDENTIALS_PATH should be credentials.json at the project root."""
    assert CREDENTIALS_PATH.name == "credentials.json"
    # The project root is three levels up from tools/gmail/auth.py
    assert CREDENTIALS_PATH.parent == CREDENTIALS_PATH.parent  # sanity
    assert not any(part in ("tools", "gmail") for part in CREDENTIALS_PATH.parts)


def test_token_path_under_app_dir() -> None:
    """TOKEN_PATH should reside inside APP_DIR."""
    assert TOKEN_PATH.parent == APP_DIR
    assert TOKEN_PATH.name == "gmail_token.json"


def test_get_credentials_raises_when_credentials_file_missing(
    tmp_path: Path,
) -> None:
    """FileNotFoundError is raised when credentials.json is absent."""
    missing = tmp_path / "credentials.json"
    with patch("tools.gmail.auth.CREDENTIALS_PATH", missing):
        with pytest.raises(FileNotFoundError, match="credentials.json not found"):
            get_credentials()


def test_get_credentials_returns_valid_existing_token(tmp_path: Path) -> None:
    """When a valid token file exists, it is returned without launching a flow."""
    fake_creds = MagicMock()
    fake_creds.valid = True

    fake_credentials_path = tmp_path / "credentials.json"
    fake_credentials_path.write_text("{}")  # content doesn't matter — not read

    with (
        patch("tools.gmail.auth.CREDENTIALS_PATH", fake_credentials_path),
        patch("tools.gmail.auth.TOKEN_PATH", tmp_path / "token.json"),
        patch(
            "tools.gmail.auth.Credentials.from_authorized_user_file",
            return_value=fake_creds,
        ),
    ):
        # Make the token file exist so the branch is taken
        (tmp_path / "token.json").write_text("{}")
        result = get_credentials()

    assert result is fake_creds
    fake_creds.refresh.assert_not_called()


def test_get_credentials_refreshes_expired_token(tmp_path: Path) -> None:
    """Expired credentials with a refresh_token are refreshed and saved."""
    fake_creds = MagicMock()
    fake_creds.valid = False
    fake_creds.expired = True
    fake_creds.refresh_token = "some-refresh-token"
    fake_creds.to_json.return_value = '{"token": "refreshed"}'

    fake_credentials_path = tmp_path / "credentials.json"
    fake_credentials_path.write_text("{}")
    token_path = tmp_path / "token.json"
    token_path.write_text("{}")

    with (
        patch("tools.gmail.auth.CREDENTIALS_PATH", fake_credentials_path),
        patch("tools.gmail.auth.TOKEN_PATH", token_path),
        patch("tools.gmail.auth.APP_DIR", tmp_path),
        patch(
            "tools.gmail.auth.Credentials.from_authorized_user_file",
            return_value=fake_creds,
        ),
        patch("tools.gmail.auth.Request") as mock_request,
    ):
        result = get_credentials()

    fake_creds.refresh.assert_called_once_with(mock_request.return_value)
    assert token_path.read_text() == '{"token": "refreshed"}'
    assert result is fake_creds
