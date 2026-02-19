"""Tests for tools/calendar/client.py — Calendar API wrapper."""

from unittest.mock import MagicMock, patch

from tools.calendar.client import (
    fetch_event_stubs,
    fetch_todays_events,
    get_service,
    parse_event,
)


def _make_service(items: list[dict] | None = None) -> MagicMock:
    """Build a mock Calendar service whose list() call returns *items*."""
    service = MagicMock()
    list_result = {"items": items} if items is not None else {}
    (service.events.return_value.list.return_value.execute.return_value) = list_result
    return service


# ---------------------------------------------------------------------------
# get_service
# ---------------------------------------------------------------------------


def test_get_service_calls_calendar_v3() -> None:
    """get_service calls build('calendar', 'v3', credentials=...) ."""
    mock_creds = MagicMock()

    with patch("tools.calendar.client.build") as mock_build:
        get_service(mock_creds)

    mock_build.assert_called_once_with("calendar", "v3", credentials=mock_creds)


# ---------------------------------------------------------------------------
# fetch_event_stubs
# ---------------------------------------------------------------------------


def test_fetch_event_stubs_returns_items() -> None:
    """fetch_event_stubs returns the list of items from the API."""
    service = _make_service(items=[{"id": "evt1"}, {"id": "evt2"}])

    result = fetch_event_stubs(
        service, "2026-02-19T00:00:00+00:00", "2026-02-19T23:59:59+00:00"
    )

    assert result == [{"id": "evt1"}, {"id": "evt2"}]


def test_fetch_event_stubs_empty_when_no_items_key() -> None:
    """fetch_event_stubs returns [] when API response has no 'items' key."""
    service = MagicMock()
    service.events.return_value.list.return_value.execute.return_value = {}

    result = fetch_event_stubs(
        service, "2026-02-19T00:00:00+00:00", "2026-02-19T23:59:59+00:00"
    )

    assert result == []


def test_fetch_event_stubs_passes_correct_params() -> None:
    """fetch_event_stubs passes singleEvents, orderBy, and calendarId correctly."""
    service = _make_service(items=[])
    time_min = "2026-02-19T00:00:00+00:00"
    time_max = "2026-02-19T23:59:59+00:00"

    fetch_event_stubs(service, time_min, time_max)

    service.events.return_value.list.assert_called_once_with(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
    )


# ---------------------------------------------------------------------------
# parse_event
# ---------------------------------------------------------------------------


def test_parse_event_datetime_fields() -> None:
    """parse_event extracts dateTime for timed events."""
    event = {
        "summary": "Team standup",
        "start": {"dateTime": "2026-02-19T09:00:00+00:00"},
        "end": {"dateTime": "2026-02-19T09:30:00+00:00"},
        "location": "Room A",
        "description": "Daily sync",
    }

    result = parse_event(event)

    assert result["summary"] == "Team standup"
    assert result["start"] == "2026-02-19T09:00:00+00:00"
    assert result["end"] == "2026-02-19T09:30:00+00:00"
    assert result["location"] == "Room A"
    assert result["description"] == "Daily sync"


def test_parse_event_all_day_fields() -> None:
    """parse_event falls back to date for all-day events."""
    event = {
        "summary": "Company holiday",
        "start": {"date": "2026-02-19"},
        "end": {"date": "2026-02-20"},
    }

    result = parse_event(event)

    assert result["summary"] == "Company holiday"
    assert result["start"] == "2026-02-19"
    assert result["end"] == "2026-02-20"
    assert result["location"] == ""
    assert result["description"] == ""


def test_parse_event_defaults_for_missing_fields() -> None:
    """parse_event uses safe defaults when fields are absent."""
    result = parse_event({})

    assert result["summary"] == "(no title)"
    assert result["start"] == ""
    assert result["end"] == ""
    assert result["location"] == ""
    assert result["description"] == ""


# ---------------------------------------------------------------------------
# fetch_todays_events
# ---------------------------------------------------------------------------


def test_fetch_todays_events_assembles_results() -> None:
    """fetch_todays_events assembles results via get_service, bounds, and stubs."""
    mock_creds = MagicMock()
    stub1 = {
        "summary": "Meeting",
        "start": {"dateTime": "2026-02-19T10:00:00+00:00"},
        "end": {"dateTime": "2026-02-19T11:00:00+00:00"},
    }
    stub2 = {
        "summary": "Lunch",
        "start": {"date": "2026-02-19"},
        "end": {"date": "2026-02-19"},
    }

    with (
        patch("tools.calendar.client.get_service") as mock_get_service,
        patch(
            "tools.calendar.client._today_bounds",
            return_value=("2026-02-19T00:00:00+00:00", "2026-02-19T23:59:59+00:00"),
        ),
        patch(
            "tools.calendar.client.fetch_event_stubs",
            return_value=[stub1, stub2],
        ) as mock_stubs,
    ):
        result = fetch_todays_events(mock_creds)

    mock_get_service.assert_called_once_with(mock_creds)
    assert mock_stubs.call_count == 1
    assert len(result) == 2
    assert result[0]["summary"] == "Meeting"
    assert result[1]["summary"] == "Lunch"
