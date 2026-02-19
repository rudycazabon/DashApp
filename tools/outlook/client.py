"""Thin wrapper around the Microsoft Graph API for mail."""

from datetime import datetime, timezone
from typing import Any, cast

import requests

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def fetch_messages(token: str, time_min: str) -> list[dict[str, Any]]:
    """Return raw message dicts from Graph API filtered by receivedDateTime >= time_min.

    Args:
        token: A valid Microsoft Graph access token.
        time_min: ISO 8601 UTC datetime string, e.g. ``"2026-02-19T00:00:00Z"``.

    Raises:
        requests.HTTPError: On a non-2xx response from the Graph API.
    """
    resp = requests.get(
        f"{GRAPH_BASE}/me/messages",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "$filter": f"receivedDateTime ge {time_min}",
            "$orderby": "receivedDateTime desc",
            "$top": "50",
            "$select": "from,subject,receivedDateTime,bodyPreview",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return cast(list[dict[str, Any]], resp.json().get("value", []))


def parse_message(msg: dict[str, Any]) -> dict[str, str]:
    """Convert a raw Graph message dict to a flat display dict.

    Returns a dict with keys: ``from_``, ``subject``, ``time``, ``snippet``.
    """
    from_address = (
        msg.get("from", {}).get("emailAddress", {}).get("address", "(unknown)")
    )
    return {
        "from_": from_address,
        "subject": msg.get("subject") or "(no subject)",
        "time": msg.get("receivedDateTime", ""),
        "snippet": msg.get("bodyPreview", ""),
    }


def _today_utc_str() -> str:
    """Return ISO 8601 UTC midnight for today, e.g. ``"2026-02-19T00:00:00Z"``."""
    today = datetime.now(timezone.utc).date()
    return f"{today}T00:00:00Z"


def fetch_todays_messages(token: str) -> list[dict[str, str]]:
    """Return messages received today as a list of flat display dicts.

    Each dict has keys: ``from_``, ``subject``, ``time``, ``snippet``.
    """
    time_min = _today_utc_str()
    raw = fetch_messages(token, time_min)
    return [parse_message(m) for m in raw]
