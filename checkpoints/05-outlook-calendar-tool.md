# Checkpoint 05 — Outlook Calendar Tool Plugin

**Date:** 2026-02-19

## What was done

Added an Outlook Calendar tool plugin using the Microsoft Graph `calendarView` endpoint.
Follows the same plugin pattern as Google Calendar and reuses `outlook_credentials.json`.

## New files

| File | Description |
|---|---|
| `tools/outlook_calendar/__init__.py` | Empty package marker |
| `tools/outlook_calendar/manifest.json` | Plugin metadata (name: "Outlook Calendar") |
| `tools/outlook_calendar/auth.py` | MSAL token flow with `Calendars.Read` scope |
| `tools/outlook_calendar/client.py` | Graph `/me/calendarView` wrapper via `requests` |
| `tools/outlook_calendar/tool.py` | `OutlookCalendarWidget` + `Tool(BaseTool)` |
| `tests/test_outlook_calendar_auth.py` | 5 auth tests |
| `tests/test_outlook_calendar_client.py` | 9 client tests |

## Architecture notes

- **Auth:** Same `outlook_credentials.json` as Outlook mail, but separate token cache at
  `~/.dashapp/outlook_calendar_token.json` with `Calendars.Read` scope.
- **Client:** Uses Graph `calendarView` endpoint (returns events overlapping time window).
  Filters today with UTC bounds `T00:00:00Z` → `T23:59:59Z`.
  Handles both timed events (`dateTime`) and all-day events (`date` + `isAllDay: True`).
- **Widget:** Mirrors `CalendarWidget` — `HH:MM — Summary` titles, `Start/End/Location/Notes` body.
  Detects all-day events via `is_all_day` flag from `parse_event`.

## Test results

```
68 passed in 1.93s
```

(54 pre-existing + 14 new Outlook Calendar tests)

## No new dependencies

Reuses `msal` and `requests` added in checkpoint 04.
