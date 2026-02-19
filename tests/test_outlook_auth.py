"""Tests for tools/outlook/auth.py — MSAL token management."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tools.outlook.auth import CREDENTIALS_PATH, TOKEN_PATH, get_access_token
from util.paths import APP_DIR


def test_credentials_path_under_app_dir() -> None:
    """CREDENTIALS_PATH should be outlook_credentials.json inside APP_DIR."""
    assert CREDENTIALS_PATH.name == "outlook_credentials.json"
    assert CREDENTIALS_PATH.parent == APP_DIR


def test_token_path_under_app_dir() -> None:
    """TOKEN_PATH should reside inside APP_DIR."""
    assert TOKEN_PATH.parent == APP_DIR
    assert TOKEN_PATH.name == "outlook_token.json"


def test_get_access_token_raises_when_credentials_file_missing(
    tmp_path: Path,
) -> None:
    """FileNotFoundError is raised when outlook_credentials.json is absent."""
    missing = tmp_path / "outlook_credentials.json"
    with patch("tools.outlook.auth.CREDENTIALS_PATH", missing):
        with pytest.raises(
            FileNotFoundError, match="outlook_credentials.json not found"
        ):
            get_access_token()


def test_get_access_token_uses_silent_flow_when_cache_has_account(
    tmp_path: Path,
) -> None:
    """When the token cache has an account, acquire_token_silent is used."""
    fake_creds_path = tmp_path / "outlook_credentials.json"
    fake_creds_path.write_text('{"client_id": "fake-id", "tenant_id": "consumers"}')

    mock_account = MagicMock()
    mock_app = MagicMock()
    mock_app.get_accounts.return_value = [mock_account]
    mock_app.acquire_token_silent.return_value = {"access_token": "silent-token"}

    mock_cache = MagicMock()
    mock_cache.has_state_changed = False

    with (
        patch("tools.outlook.auth.CREDENTIALS_PATH", fake_creds_path),
        patch("tools.outlook.auth.TOKEN_PATH", tmp_path / "outlook_token.json"),
        patch(
            "tools.outlook.auth.msal.SerializableTokenCache", return_value=mock_cache
        ),
        patch("tools.outlook.auth.msal.PublicClientApplication", return_value=mock_app),
    ):
        token = get_access_token()

    assert token == "silent-token"
    mock_app.acquire_token_silent.assert_called_once_with(
        ["Mail.Read"], account=mock_account
    )
    mock_app.acquire_token_interactive.assert_not_called()


def test_get_access_token_uses_interactive_flow_when_no_cache(
    tmp_path: Path,
) -> None:
    """When no cached accounts exist, acquire_token_interactive is used."""
    fake_creds_path = tmp_path / "outlook_credentials.json"
    fake_creds_path.write_text('{"client_id": "fake-id"}')

    mock_app = MagicMock()
    mock_app.get_accounts.return_value = []
    mock_app.acquire_token_interactive.return_value = {
        "access_token": "interactive-token"
    }

    mock_cache = MagicMock()
    mock_cache.has_state_changed = True
    mock_cache.serialize.return_value = '{"cache": "data"}'

    with (
        patch("tools.outlook.auth.CREDENTIALS_PATH", fake_creds_path),
        patch("tools.outlook.auth.TOKEN_PATH", tmp_path / "outlook_token.json"),
        patch("tools.outlook.auth.APP_DIR", tmp_path),
        patch(
            "tools.outlook.auth.msal.SerializableTokenCache", return_value=mock_cache
        ),
        patch("tools.outlook.auth.msal.PublicClientApplication", return_value=mock_app),
    ):
        token = get_access_token()

    assert token == "interactive-token"
    mock_app.acquire_token_silent.assert_not_called()
    mock_app.acquire_token_interactive.assert_called_once_with(scopes=["Mail.Read"])
    # Cache should have been serialized to disk
    saved = (tmp_path / "outlook_token.json").read_text()
    assert saved == '{"cache": "data"}'
