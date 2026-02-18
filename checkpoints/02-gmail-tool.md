# Checkpoint 02 — Gmail Tool

**Date:** 2026-02-18
**Status:** Complete

## What was built

A Gmail plugin for DashApp that displays today's emails in a dedicated tab. The plugin follows the established `tools/<name>/` layout.

## Files created

| File | Purpose |
|---|---|
| `tools/gmail/__init__.py` | Package marker |
| `tools/gmail/manifest.json` | Plugin metadata |
| `tools/gmail/auth.py` | OAuth 2.0 flow — load/refresh/issue token |
| `tools/gmail/client.py` | Gmail API wrapper — `get_service`, `fetch_todays_emails` |
| `tools/gmail/tool.py` | `GmailWidget(Widget)` + `Tool(BaseTool)` |
| `tests/test_gmail_auth.py` | 5 unit tests for auth (all mocked) |
| `tests/test_gmail_client.py` | 4 unit tests for API client (all mocked) |

## Files modified

- `.gitignore` — added `credentials.json`, `gmail_token.json`, `*.apps.googleusercontent.com.json`
- `pyproject.toml` — updated by `uv add` with 23 new packages

## Key design decisions

- **`auth.py` / `client.py` split** — auth logic independently testable
- **`thread=True` worker** — Gmail I/O runs off Textual's async event loop
- **`self.app.call_from_thread()`** — UI mutations dispatched to main thread (avoids `call_from_thread` being unknown on `Widget*` in pyright)
- **Return `Any` from `get_service`** — googleapiclient uses dynamic attrs that pyright can't resolve statically
- **`cast(Credentials, flow.run_local_server(...))`** — `InstalledAppFlow` returns a union type; cast narrows it to `google.oauth2.credentials.Credentials`
- **Token at `~/.dashapp/gmail_token.json`** — consistent with `APP_DIR` convention; never committed
- **`credentials.json` at project root** — user's placement; added to `.gitignore`
- **Metadata-only fetch** — faster than full message; only From/Subject/Date/Snippet needed
- **Errors surface in widget** — broken auth/network shows inline error; app keeps running

## OAuth credential locations

- `credentials.json` — project root (OAuth client ID, downloaded from Google Cloud Console)
- `~/.dashapp/gmail_token.json` — persisted token written after first browser auth

## Test results

```
27 passed in 0.89s
```

All 27 tests pass (18 pre-existing + 9 new Gmail tests).

## Quality checks

- `ruff format` — clean
- `ruff check` — 0 errors
- `pyright` — 0 errors, 0 warnings

## First-run flow

1. User runs `uv run dashapp`
2. Gmail tab appears; widget mounts and spawns worker thread
3. Worker calls `get_credentials()` → no token yet → opens browser for OAuth consent
4. Token saved to `~/.dashapp/gmail_token.json`
5. Emails fetched and displayed in DataTable
6. Subsequent runs use cached token (refresh if expired)
