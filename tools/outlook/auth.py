"""OAuth token management for the Outlook tool via MSAL PublicClientApplication."""

import json
from typing import Any

import msal

from util.paths import APP_DIR, OUTLOOK_CREDENTIALS_PATH

SCOPES = ["Mail.Read"]
TOKEN_PATH = APP_DIR / "outlook_token.json"
CREDENTIALS_PATH = OUTLOOK_CREDENTIALS_PATH


def get_access_token() -> str:
    """Return a valid Microsoft Graph access token, using cache or interactive flow.

    Raises:
        FileNotFoundError: When outlook_credentials.json is absent from ~/.dashapp/.
        RuntimeError: When MSAL cannot acquire a token.
    """
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"outlook_credentials.json not found at {CREDENTIALS_PATH}. "
            "Register an Azure app and place the file in ~/.dashapp/."
        )

    cred_data: dict[str, Any] = json.loads(CREDENTIALS_PATH.read_text())
    client_id: str = cred_data["client_id"]
    tenant_id: str = cred_data.get("tenant_id", "consumers")
    authority = f"https://login.microsoftonline.com/{tenant_id}"

    cache = msal.SerializableTokenCache()
    if TOKEN_PATH.exists():
        cache.deserialize(TOKEN_PATH.read_text())

    app = msal.PublicClientApplication(
        client_id, authority=authority, token_cache=cache
    )

    result: dict[str, Any] | None = None
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])

    if not result:
        result = app.acquire_token_interactive(scopes=SCOPES)

    # result is always a dict after acquire_token_interactive (never None)
    token_result: dict[str, Any] = result or {}
    if "access_token" not in token_result:
        description = token_result.get(
            "error_description", token_result.get("error", "unknown")
        )
        raise RuntimeError(f"Could not acquire Outlook token: {description}")

    if cache.has_state_changed:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(cache.serialize())

    return str(token_result["access_token"])
