"""Thin wrapper around the Microsoft Graph API for calendar events."""

from datetime import datetime, timezone
from typing import Any, cast

import requests

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def fetch_events(token: str, time_min: str, time_max: str) -> list[dict[str, Any]]:
    """Return raw event dicts from the Graph calendarView endpoint.

    Args:
        token: A valid Microsoft Graph access token with Calendars.Read scope.
        time_min: ISO 8601 UTC start datetime, e.g. ``"2026-02-19T00:00:00Z"``.
        time_max: ISO 8601 UTC end datetime, e.g. ``"2026-02-19T23:59:59Z"``.

    Raises:
        requests.HTTPError: On a non-2xx response from the Graph API.
    """
    resp = requests.get(
        f"{GRAPH_BASE}/me/calendarView",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "startDateTime": time_min,
            "endDateTime": time_max,
            "$orderby": "start/dateTime",
            "$top": "50",
            "$select": "subject,start,end,location,bodyPreview,isAllDay",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return cast(list[dict[str, Any]], resp.json().get("value", []))


def parse_event(event: dict[str, Any]) -> dict[str, str]:
    """Convert a raw Graph calendar event to a flat display dict.

    Returns a dict with keys: ``summary``, ``start``, ``end``,
    ``location``, ``description``, ``is_all_day``.
    """
    start_obj = event.get("start", {})
    end_obj = event.get("end", {})
    location_obj = event.get("location", {})
    return {
        "summary": event.get("subject") or "(no title)",
        "start": start_obj.get("dateTime", start_obj.get("date", "")),
        "end": end_obj.get("dateTime", end_obj.get("date", "")),
        "location": location_obj.get("displayName", "") if location_obj else "",
        "description": event.get("bodyPreview", ""),
        "is_all_day": str(event.get("isAllDay", False)),
    }


def _today_bounds_utc() -> tuple[str, str]:
    """Return ISO 8601 UTC start and end strings for today.

    Returns ``("YYYY-MM-DDT00:00:00Z", "YYYY-MM-DDT23:59:59Z")``.
    """
    today = datetime.now(timezone.utc).date()
    return f"{today}T00:00:00Z", f"{today}T23:59:59Z"


def fetch_todays_events(token: str) -> list[dict[str, str]]:
    """Return today's calendar events as a list of flat display dicts.

    Each dict has keys: ``summary``, ``start``, ``end``,
    ``location``, ``description``, ``is_all_day``.
    """
    time_min, time_max = _today_bounds_utc()
    raw = fetch_events(token, time_min, time_max)
    return [parse_event(e) for e in raw]
