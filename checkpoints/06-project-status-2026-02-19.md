# Checkpoint 06 — Full Project Status

**Date:** 2026-02-19
**Branch:** main
**HEAD:** 3d1be6c

---

## Overview

DashApp is a cross-platform Python TUI dashboard built on [Textual](https://textual.textualize.io/).
It uses a plugin architecture where each tool lives in `tools/<name>/` and is automatically
discovered and loaded at startup. Four personal productivity tools are fully implemented.

---

## What is complete

### Core framework (checkpoint 01)
- Plugin loader (`loader.py`) — discovers `tools/<name>/manifest.json` + `tool.py`
- SQLite config/state store (`db/manager.py`, `config.py`) at `~/.dashapp/dashapp.db`
- TUI shell (`tui/app.py`) — `TabbedContent` with Home tab + one tab per loaded tool
- Shared paths (`util/paths.py`) — `APP_DIR`, `DB_PATH`, `LOGS_DIR`
- Entry point: `main.py` → `uv run python main.py`
- Demo tool (`tools/demo/`) included as a smoke-test plugin

### Gmail tool (checkpoints 02 + 03)
- OAuth via `google-auth-oauthlib` (`InstalledAppFlow`), token cached at `~/.dashapp/gmail_token.json`
- Credentials: `credentials.json` at project root (Google Cloud Console download, gitignored)
- Fetches today's messages (up to 50) via Gmail API v1
- `GmailWidget`: progress bar, collapsible rows `Subject — From`, body shows From/Date/Snippet
- Widget redesigned: fixed blank-tab bug, added progress bar + collapsible emails

### Google Calendar tool (checkpoint 03)
- Same Google OAuth credentials (`credentials.json`), token at `~/.dashapp/calendar_token.json`
- Fetches today's events from primary calendar via Calendar API v3
- `CalendarWidget`: `HH:MM — Summary` or `All day — Summary` titles, body shows Start/End/Location/Notes

### Outlook Mail tool (checkpoint 04)
- MSAL `PublicClientApplication` (no client secret), token at `~/.dashapp/outlook_token.json`
- Scope: `Mail.Read`
- Credentials: `outlook_credentials.json` at project root (gitignored)
- Fetches today's messages (up to 50) via Graph `/me/messages` filtered by `receivedDateTime`
- `OutlookWidget`: mirrors GmailWidget exactly

### Outlook Calendar tool (checkpoint 05)
- Same `outlook_credentials.json`, separate token at `~/.dashapp/outlook_calendar_token.json`
- Scope: `Calendars.Read`
- Fetches today's events via Graph `/me/calendarView` with UTC `T00:00:00Z`→`T23:59:59Z` bounds
- `OutlookCalendarWidget`: mirrors CalendarWidget; handles `isAllDay` flag from Graph

---

## Project structure

```
DashApp/
├── main.py                         # entry point
├── config.py                       # Config wrapper (get/set over SQLite)
├── loader.py                       # plugin discovery
├── pyproject.toml
├── tools/
│   ├── base.py                     # BaseTool ABC
│   ├── demo/                       # smoke-test plugin
│   ├── gmail/                      # Gmail mail
│   ├── calendar/                   # Google Calendar
│   ├── outlook/                    # Outlook mail
│   └── outlook_calendar/           # Outlook Calendar
├── tui/
│   ├── app.py                      # DashApp(App[None])
│   └── screens/home.py             # HomeScreen widget
├── db/manager.py                   # SQLite helpers
├── util/paths.py                   # APP_DIR, DB_PATH, LOGS_DIR
└── tests/                          # 68 tests, all passing
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `textual` + `textual-dev` + `textual[syntax]` | TUI framework |
| `google-auth-oauthlib` | Google OAuth flow |
| `google-auth-httplib2` | Google HTTP transport |
| `google-api-python-client` | Gmail + Calendar APIs |
| `msal` | Microsoft MSAL for Outlook OAuth |
| `requests` | HTTP client for Graph API |

---

## Credentials required (first run)

| Tool | File | How to obtain |
|---|---|---|
| Gmail | `credentials.json` (project root) | Google Cloud Console → OAuth 2.0 client ID |
| Google Calendar | `credentials.json` (same file) | Same as Gmail |
| Outlook Mail | `outlook_credentials.json` (project root) | Azure Portal → App registrations |
| Outlook Calendar | `outlook_credentials.json` (same file) | Same as Outlook Mail |

`outlook_credentials.json` format:
```json
{"client_id": "<Azure app client ID>", "tenant_id": "consumers"}
```

Azure app requirements: Personal Microsoft accounts only, Redirect URI `http://localhost`
(Mobile/desktop app type).

---

## Test suite

```
68 passed in 0.83s
```

| Test file | Tests | Covers |
|---|---|---|
| `test_db_manager.py` | 6 | SQLite helpers |
| `test_config.py` | 5 | Config get/set/persist |
| `test_loader.py` | 7 | Plugin discovery |
| `test_gmail_auth.py` | 5 | Google OAuth flow |
| `test_gmail_client.py` | 10 | Gmail API wrapper |
| `test_calendar_client.py` | 8 | Calendar API wrapper |
| `test_outlook_auth.py` | 5 | MSAL mail token flow |
| `test_outlook_client.py` | 8 | Graph mail wrapper |
| `test_outlook_calendar_auth.py` | 5 | MSAL calendar token flow |
| `test_outlook_calendar_client.py` | 9 | Graph calendar wrapper |

---

## Running

```bash
# preferred
uv sync && uv run dashapp

# fallback (if script not installed)
uv run python main.py
```

---

## Known issues / next steps

- `uv run dashapp` may fail if `uv sync` has not been run after checkout — run `uv sync` first
- No Outlook Calendar auth test for the widget itself (widget tests require a Textual pilot)
- Mobile / web client not yet started (future milestone)
