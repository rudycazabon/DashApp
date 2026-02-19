# Checkpoint 03 — Google Calendar Tool

**Date:** 2026-02-19
**Status:** Complete

## What Was Done

Added a Google Calendar tool plugin following the same plugin pattern as the Gmail tool.

## Files Created

| File | Description |
|---|---|
| `tools/calendar/__init__.py` | Empty package marker |
| `tools/calendar/manifest.json` | Plugin metadata (name, version, description, author) |
| `tools/calendar/auth.py` | OAuth 2.0 with `calendar.readonly` scope; token at `~/.dashapp/calendar_token.json` |
| `tools/calendar/client.py` | `get_service`, `_today_bounds`, `fetch_event_stubs`, `parse_event`, `fetch_todays_events` |
| `tools/calendar/tool.py` | `CalendarWidget` + `Tool(BaseTool)` |
| `tests/test_calendar_client.py` | 8 tests covering all client functions |

## Key Design Decisions

- `_today_bounds()` computes local-timezone RFC 3339 start/end for today
- `parse_event()` is a pure function — handles both timed (`dateTime`) and all-day (`date`) events
- Progress: 0% → 20% (auth) → 40% (service) → 80% (stubs fetched) → 100% (parsed)
- Collapsible title format: `"HH:MM — summary"` or `"All day — summary"`

## Verification

```
uv run ruff check .     → All checks passed
uv run pyright          → 0 errors, 0 warnings
uv run pytest tests/ -v → 41 passed (33 existing + 8 new)
```
