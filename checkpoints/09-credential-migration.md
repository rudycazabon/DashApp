# Checkpoint 09 — Credential File Migration to ~/.dashapp/

**Date:** 2026-02-19
**Branch:** main

---

## What was done

Moved all credential JSON files from the project root into `~/.dashapp/` so that the
application's runtime data lives in one place and nothing sensitive is ever near the
git repository working directory.

### Changes

**`util/paths.py`** — Added three credential path constants:
```python
GOOGLE_CREDENTIALS_PATH  = APP_DIR / "credentials.json"
OUTLOOK_CREDENTIALS_PATH = APP_DIR / "outlook_credentials.json"
JIRA_CREDENTIALS_PATH    = APP_DIR / "jira_credentials.json"
```

**All 5 `auth.py` modules** — `CREDENTIALS_PATH` now assigned from the central constant
instead of computed relative to `__file__`. `from pathlib import Path` removed where it
was only needed for that computation.

| File | Old CREDENTIALS_PATH | New CREDENTIALS_PATH |
|---|---|---|
| `tools/gmail/auth.py` | `Path(__file__).parent.parent.parent / "credentials.json"` | `GOOGLE_CREDENTIALS_PATH` |
| `tools/calendar/auth.py` | `Path(__file__).parent.parent.parent / "credentials.json"` | `GOOGLE_CREDENTIALS_PATH` |
| `tools/outlook/auth.py` | `Path(__file__).parent.parent.parent / "outlook_credentials.json"` | `OUTLOOK_CREDENTIALS_PATH` |
| `tools/outlook_calendar/auth.py` | `Path(__file__).parent.parent.parent / "outlook_credentials.json"` | `OUTLOOK_CREDENTIALS_PATH` |
| `tools/jira/auth.py` | `Path(__file__).parent.parent.parent / "jira_credentials.json"` | `JIRA_CREDENTIALS_PATH` |

Error messages in all auth.py files updated to reference `~/.dashapp/` instead of
"project root".

**Tests** — `test_credentials_path_points_to_project_root` renamed to
`test_credentials_path_under_app_dir` in all 4 auth test files; assertion changed from
checking path parts to `CREDENTIALS_PATH.parent == APP_DIR`.

**`README.md` / `CLAUDE.md`** — Credentials setup instructions updated to reference
`~/.dashapp/` instead of project root; CLAUDE.md tool table updated with Jira row and
credential location column clarification.

---

## Files to delete from project root

The following files have been copied to `~/.dashapp/` and are safe to delete from the
project root:

| File | Moved to |
|---|---|
| `credentials.json` | `~/.dashapp/credentials.json` |
| `outlook_credentials.json` | `~/.dashapp/outlook_credentials.json` |
| `jira_credentials.json` | `~/.dashapp/jira_credentials.json` |

The following files were never loaded by DashApp code and can also be deleted:

| File | Note |
|---|---|
| `client_secret_2_*.json` | Original Google Cloud Console download; superseded by `credentials.json` |
| `mygdrive-*.json` | Google service-account key; not used by DashApp |

---

## Test suite

```
90 passed in 0.88s
```

No new tests added; 4 existing path assertion tests updated.

---

## No new dependencies
