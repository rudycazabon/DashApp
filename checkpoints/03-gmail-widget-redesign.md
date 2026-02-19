# Checkpoint 03 — Gmail Widget Redesign

**Date:** 2026-02-19

## What Was Done

Fixed blank Gmail tab and redesigned the widget with three UX features:
expandable email entries, a connection-status dot, and a progress bar.

## Problem Fixed

`GmailWidget` had no `DEFAULT_CSS`, causing it to collapse to zero height.
Neither the status label nor the DataTable were visible.

## Changes

### `tools/gmail/client.py`
- Added `fetch_message_ids(service, today_str)` — returns stub list from Gmail API
- Added `fetch_message_detail(service, msg_id)` — fetches one message by ID
- Refactored `fetch_todays_emails` into a thin wrapper calling the two new helpers
- Added `cast` import

### `tools/gmail/tool.py`
- Full rewrite of `GmailWidget`
- `DEFAULT_CSS`: sets `height: 1fr` (critical fix) + styles for status bar / scroll area
- `compose()`: status bar with red/green dot, status text, ProgressBar; VerticalScroll below
- `_load()` (worker thread): granular progress 0→20→40→100% through auth → id-list → per-message
- `_populate()` (main thread): mounts `Collapsible` per email (collapsed by default),
  updates dot to green, hides progress bar
- `_show_error()` (main thread): updates dot/text, hides progress bar

### `tests/test_gmail_client.py`
- Added 6 new tests: `fetch_message_ids` (3) and `fetch_message_detail` (2) and
  `fetch_todays_emails` integration (1)
- Existing 4 tests unchanged

## Verification

- `uv run ruff format .` — clean
- `uv run ruff check .` — All checks passed
- `uv run pyright` — 0 errors, 0 warnings
- `uv run pytest tests/ -v` — **33 passed**
