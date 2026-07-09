# Checkpoint 13 — Confluence tool

**Date:** 2026-07-09
**Branch:** main

## Summary

Added a Confluence plugin that lists recently updated pages grouped by space,
mirroring the Jira tool's projects→issues layout. Confluence Cloud uses the same
Atlassian Basic Auth (email + API token) as Jira, so the tool follows the identical
`auth.py` / `client.py` / `tool.py` structure.

## What was added

- **`tools/confluence/`**
  - `manifest.json` — name "Confluence".
  - `auth.py` — `get_auth() -> (requests.Session, base_url)`; reads
    `~/.dashapp/confluence_credentials.json` (`url`, `email`, `api_token`).
  - `client.py` — `fetch_spaces` / `parse_space` (GET `/wiki/api/v2/spaces`) and
    `fetch_pages` / `parse_page` (GET `/wiki/api/v2/pages?sort=-modified-date`).
  - `tool.py` — `ConfluenceWidget(NavigableToolWidget)` + `Tool(BaseTool)`.
- **Tests:** `tests/test_confluence_auth.py` (6), `tests/test_confluence_client.py`
  (11) — 17 new tests.
- **`util/paths.py`:** added `CONFLUENCE_CREDENTIALS_PATH`.
- **`.gitignore`:** added `confluence_credentials.json`.
- **Docs:** `CLAUDE.md`, `README.md`, `TODO.md` updated.

## Design notes

- One `fetch_spaces` call + one `fetch_pages` call (recent pages across all
  spaces), grouped client-side by `spaceId` — same 2-request shape as Jira, rather
  than one request per space.
- Reuses `NavigableToolWidget` for Up/Down/Left/Right Collapsible navigation.
- Credentials are a separate file from Jira (per-tool convention); the same
  Atlassian API token works for both.
- The credentials `url` is the site root; the REST API path `/wiki` is appended in
  `client.py`, so `base_url` stays consistent with the Jira tool.

## Verification

- `uv run pytest tests/ -q` → **57 passed** (40 prior + 17 new)
- `uv run ruff format .` / `uv run ruff check .` → clean
- `uv run pyright` → 0 errors, 0 warnings
- Plugin auto-discovered by `loader.py` (no wiring changes); appears as a
  "Confluence" tab after Home/Demo/Jira.

## Requires (user)

Create `~/.dashapp/confluence_credentials.json`:
```json
{"url": "https://yourco.atlassian.net", "email": "you@example.com", "api_token": "<token>"}
```
