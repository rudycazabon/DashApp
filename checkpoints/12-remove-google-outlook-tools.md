# Checkpoint 12 — Remove Gmail, Google Calendar, Outlook, and Outlook Calendar tools

**Date:** 2026-07-09
**Branch:** main

## Summary

Retired the four Google/Microsoft mail-and-calendar plugins, narrowing DashApp to
the `demo` and `jira` tools. This drops the entire Google OAuth and MSAL dependency
stack. No core wiring changed — the plugin loader auto-discovers tools, so deleting
the directories was sufficient for the tabs to disappear.

## What was removed

- **Tool packages:** `tools/gmail/`, `tools/calendar/`, `tools/outlook/`,
  `tools/outlook_calendar/`
- **Tests (7 files, ~50 tests):** `test_gmail_auth.py`, `test_gmail_client.py`,
  `test_calendar_client.py`, `test_outlook_auth.py`, `test_outlook_client.py`,
  `test_outlook_calendar_auth.py`, `test_outlook_calendar_client.py`
- **Diagnostic script:** `diagnose_gmail.py`
- **Dependencies** (`pyproject.toml`): `google-auth-oauthlib`,
  `google-auth-httplib2`, `google-api-python-client`, `msal`.
  `requests` kept (Jira uses it); `textual` kept.
- **Credential constants** (`util/paths.py`): `GOOGLE_CREDENTIALS_PATH`,
  `OUTLOOK_CREDENTIALS_PATH`. `JIRA_CREDENTIALS_PATH` kept.
- **`.gitignore`:** Google and Microsoft OAuth credential-ignore blocks.

## What was updated

- `CLAUDE.md` — Implemented-tools table, project structure, and auth paragraphs now
  list only Jira.
- `README.md` — feature table, credential-setup section, project structure, test count.
- `TODO.md` — test-count note updated to 40; C02–C05 archive rows kept as history.

## What was intentionally kept

- Historical checkpoints `02-gmail-tool.md`, `03-gmail-widget-redesign.md`,
  `03-calendar-tool.md`, `04-outlook-tool.md`, `05-outlook-calendar-tool.md`.
- Runtime user files in `~/.dashapp/` (`credentials.json`, `*_token.json`,
  `outlook_credentials.json`) — outside the repo; left for the user to remove manually.

## Verification

- `uv run pytest tests/ -q` → **40 passed**
- `uv run ruff format .` → clean; `uv run ruff check .` → all checks passed
- `uv run pyright` → 0 errors, 0 warnings
- `uv.lock` regenerated: `dashapp` depends only on `requests` + `textual`; no
  google/msal packages present.
- Grep for `gmail|outlook|googleapiclient|google-auth|msal|InstalledAppFlow` outside
  `checkpoints/` returns only the historical TODO.md archive rows and this session log.
