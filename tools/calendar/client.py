"""Thin wrapper around the Google Calendar REST API."""

from datetime import datetime
from datetime import time as dt_time
from typing import Any, cast

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_service(creds: Credentials) -> Any:
    """Build and return an authenticated Calendar API service (calendar v3).

    Returns Any because googleapiclient.Resource uses dynamic attribute
    access that static type-checkers cannot resolve.
    """
    return build("calendar", "v3", credentials=creds)


def _today_bounds() -> tuple[str, str]:
    """Return RFC 3339 start and end timestamps for today in the local timezone."""
    local_now = datetime.now().astimezone()
    tz = local_now.tzinfo
    today = local_now.date()
    time_min = datetime.combine(today, dt_time.min, tzinfo=tz).isoformat()
    time_max = datetime.combine(today, dt_time.max, tzinfo=tz).isoformat()
    return time_min, time_max


def fetch_event_stubs(
    service: Any, time_min: str, time_max: str
) -> list[dict[str, Any]]:
    """Return today's events from the primary calendar as raw API dicts."""
    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return cast(list[dict[str, Any]], result.get("items", []))


def parse_event(event: dict[str, Any]) -> dict[str, str]:
    """Convert a raw Calendar API event dict to a flat display dict.

    Keys: ``summary``, ``start``, ``end``, ``location``, ``description``.
    Handles both timed events (``dateTime``) and all-day events (``date``).
    """
    start_raw = event.get("start", {})
    end_raw = event.get("end", {})
    start = start_raw.get("dateTime", start_raw.get("date", ""))
    end = end_raw.get("dateTime", end_raw.get("date", ""))
    return {
        "summary": event.get("summary", "(no title)"),
        "start": start,
        "end": end,
        "location": event.get("location", ""),
        "description": event.get("description", ""),
    }


def fetch_todays_events(creds: Credentials) -> list[dict[str, str]]:
    """Return today's calendar events as a list of flat display dicts.

    Each dict has keys: ``summary``, ``start``, ``end``, ``location``, ``description``.
    """
    service = get_service(creds)
    time_min, time_max = _today_bounds()
    stubs = fetch_event_stubs(service, time_min, time_max)
    return [parse_event(s) for s in stubs]
