"""Tests for tools/outlook_calendar/client.py — Graph calendar API wrapper."""

import re
from unittest.mock import MagicMock, patch

import pytest

from tools.outlook_calendar.client import (
    _today_bounds_utc,
    fetch_events,
    fetch_todays_events,
    parse_event,
)

# ---------------------------------------------------------------------------
# fetch_events
# ---------------------------------------------------------------------------


def test_fetch_events_returns_value() -> None:
    """fetch_events returns the 'value' list from the JSON response."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"value": [{"id": "e1"}, {"id": "e2"}]}

    with patch("tools.outlook_calendar.client.requests.get", return_value=mock_resp):
        result = fetch_events("token", "2026-02-19T00:00:00Z", "2026-02-19T23:59:59Z")

    assert result == [{"id": "e1"}, {"id": "e2"}]
    mock_resp.raise_for_status.assert_called_once()


def test_fetch_events_empty_when_no_value_key() -> None:
    """fetch_events returns [] when 'value' key is absent from response."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {}

    with patch("tools.outlook_calendar.client.requests.get", return_value=mock_resp):
        result = fetch_events("token", "2026-02-19T00:00:00Z", "2026-02-19T23:59:59Z")

    assert result == []


def test_fetch_events_passes_correct_params() -> None:
    """fetch_events sends startDateTime, endDateTime, and Authorization header."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"value": []}

    with patch(
        "tools.outlook_calendar.client.requests.get", return_value=mock_resp
    ) as mock_get:
        fetch_events("my-token", "2026-02-19T00:00:00Z", "2026-02-19T23:59:59Z")

    _, kwargs = mock_get.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer my-token"
    params = kwargs["params"]
    assert params["startDateTime"] == "2026-02-19T00:00:00Z"
    assert params["endDateTime"] == "2026-02-19T23:59:59Z"
    assert "$orderby" in params
    assert "$top" in params
    assert "$select" in params


def test_fetch_events_raises_on_http_error() -> None:
    """fetch_events propagates HTTPError raised by raise_for_status."""
    import requests as req_lib

    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = req_lib.HTTPError("403")

    with patch("tools.outlook_calendar.client.requests.get", return_value=mock_resp):
        with pytest.raises(req_lib.HTTPError):
            fetch_events("token", "2026-02-19T00:00:00Z", "2026-02-19T23:59:59Z")


# ---------------------------------------------------------------------------
# parse_event
# ---------------------------------------------------------------------------


def test_parse_event_normal_fields() -> None:
    """parse_event maps Graph event fields to the flat display dict."""
    event = {
        "subject": "Team standup",
        "start": {"dateTime": "2026-02-19T09:00:00.0000000"},
        "end": {"dateTime": "2026-02-19T09:30:00.0000000"},
        "location": {"displayName": "Conference Room A"},
        "bodyPreview": "Daily sync",
        "isAllDay": False,
    }
    result = parse_event(event)
    assert result["summary"] == "Team standup"
    assert result["start"] == "2026-02-19T09:00:00.0000000"
    assert result["end"] == "2026-02-19T09:30:00.0000000"
    assert result["location"] == "Conference Room A"
    assert result["description"] == "Daily sync"
    assert result["is_all_day"] == "False"


def test_parse_event_all_day_fields() -> None:
    """parse_event handles all-day events that use 'date' instead of 'dateTime'."""
    event = {
        "subject": "Company Holiday",
        "start": {"date": "2026-02-19"},
        "end": {"date": "2026-02-20"},
        "location": {},
        "bodyPreview": "",
        "isAllDay": True,
    }
    result = parse_event(event)
    assert result["summary"] == "Company Holiday"
    assert result["start"] == "2026-02-19"
    assert result["end"] == "2026-02-20"
    assert result["is_all_day"] == "True"


def test_parse_event_defaults_for_missing_fields() -> None:
    """parse_event uses safe defaults when fields are absent."""
    result = parse_event({})
    assert result["summary"] == "(no title)"
    assert result["start"] == ""
    assert result["end"] == ""
    assert result["location"] == ""
    assert result["description"] == ""
    assert result["is_all_day"] == "False"


# ---------------------------------------------------------------------------
# _today_bounds_utc
# ---------------------------------------------------------------------------


def test_today_bounds_utc_format() -> None:
    """_today_bounds_utc returns two strings matching the expected UTC patterns."""
    start, end = _today_bounds_utc()
    assert re.match(r"^\d{4}-\d{2}-\d{2}T00:00:00Z$", start)
    assert re.match(r"^\d{4}-\d{2}-\d{2}T23:59:59Z$", end)
    # Both should be the same calendar date
    assert start[:10] == end[:10]


# ---------------------------------------------------------------------------
# fetch_todays_events
# ---------------------------------------------------------------------------


def test_fetch_todays_events_assembles_results() -> None:
    """fetch_todays_events calls fetch_events and parse_event for each item."""
    raw = [{"id": "e1"}, {"id": "e2"}]
    parsed = [
        {
            "summary": "Meeting",
            "start": "T1",
            "end": "T2",
            "location": "",
            "description": "",
            "is_all_day": "False",
        },
        {
            "summary": "Lunch",
            "start": "T3",
            "end": "T4",
            "location": "Cafe",
            "description": "",
            "is_all_day": "False",
        },
    ]

    with (
        patch(
            "tools.outlook_calendar.client.fetch_events", return_value=raw
        ) as mock_fetch,
        patch(
            "tools.outlook_calendar.client.parse_event", side_effect=parsed
        ) as mock_parse,
        patch(
            "tools.outlook_calendar.client._today_bounds_utc",
            return_value=("2026-02-19T00:00:00Z", "2026-02-19T23:59:59Z"),
        ),
    ):
        result = fetch_todays_events("token")

    mock_fetch.assert_called_once_with(
        "token", "2026-02-19T00:00:00Z", "2026-02-19T23:59:59Z"
    )
    assert mock_parse.call_count == 2
    assert result == parsed
