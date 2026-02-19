# Checkpoint 07 — Jira Tool Plugin

**Date:** 2026-02-19

## What was done

Added a Jira tool plugin using the Jira REST API v3 with Basic Auth (email + API token).
Displays open issues grouped by project in a nested collapsible tree.
Also hardened `.gitignore` to cover all sensitive credential files.

## New files

| File | Description |
|---|---|
| `tools/jira/__init__.py` | Empty package marker |
| `tools/jira/manifest.json` | Plugin metadata (name: "Jira") |
| `tools/jira/auth.py` | Reads `jira_credentials.json`; returns `(session, base_url)` |
| `tools/jira/client.py` | `fetch_projects`, `parse_project`, `fetch_issues`, `parse_issue` |
| `tools/jira/tool.py` | `JiraWidget` + `Tool(BaseTool)` |
| `tests/test_jira_auth.py` | 5 auth tests |
| `tests/test_jira_client.py` | 11 client tests |

## Architecture notes

- **Auth:** Basic Auth via `requests.Session` (no OAuth flow). Credentials read from
  `jira_credentials.json` at project root (gitignored).
  Format: `{"url": "https://xxx.atlassian.net", "email": "...", "api_token": "..."}`.
  No token caching needed — API tokens don't expire.
- **Client:** Two API calls: `GET /rest/api/3/project/search` (up to 50 projects), then
  a single JQL query `GET /rest/api/3/search` for all open issues across those projects
  (`statusCategory != Done`, up to 200 issues). Issues grouped by project key in Python.
- **Widget:** Nested Collapsibles — outer per project (`KEY — Name (N open)`), inner per
  issue (`ISSUE-123 — Summary [Status]`). Each project shows "No open issues." if empty.
  Status bar shows total projects + total open issues count.

## .gitignore additions

Added: `outlook_credentials.json`, `azure.txt`, `jira_credentials.json`,
`atlassian.txt`, `atlassian.ps1`, `mygdrive-*.json`.

## Credentials setup

Create `jira_credentials.json` at the project root:
```json
{"url": "https://yourcompany.atlassian.net", "email": "you@example.com", "api_token": "your-api-token"}
```
Get an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

## Test results

```
84 passed in 0.89s
```

(68 pre-existing + 16 new Jira tests)

## No new dependencies

Reuses `requests` already present from Outlook tools.
