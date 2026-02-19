# Checkpoint 04 — Outlook Mail Tool Plugin

**Date:** 2026-02-19

## What was done

Added a personal Outlook mail tool following the same plugin pattern as Gmail/Calendar.

## New files

| File | Description |
|---|---|
| `tools/outlook/__init__.py` | Empty package marker |
| `tools/outlook/manifest.json` | Plugin metadata |
| `tools/outlook/auth.py` | MSAL PublicClientApplication OAuth token flow |
| `tools/outlook/client.py` | Microsoft Graph API wrapper via `requests` |
| `tools/outlook/tool.py` | OutlookWidget + Tool(BaseTool) |
| `tests/test_outlook_auth.py` | 5 auth tests |
| `tests/test_outlook_client.py` | 8 client tests |

## New dependencies

- `msal==1.34.0` — Microsoft Authentication Library
- `requests` (already present transitively, now explicit)

## Architecture notes

- **Auth:** `msal.PublicClientApplication` (no client secret — public installed app for personal accounts). Token cache serialized to `~/.dashapp/outlook_token.json`.
- **Client:** Pure functions using `requests.get` against `https://graph.microsoft.com/v1.0/me/messages`. No service object.
- **Widget:** Identical structure to `GmailWidget` — progress bar, collapsible email rows, green/red status dot.
- **Credentials:** `outlook_credentials.json` at project root (gitignored). Format: `{"client_id": "...", "tenant_id": "consumers"}`.

## Test results

```
54 passed in 1.34s
```

(41 pre-existing + 13 new Outlook tests)

## User setup required

1. Register app in Azure Portal → App registrations
2. Set "Personal Microsoft accounts only" account type
3. Add Redirect URI: Mobile/desktop → `http://localhost`
4. Copy Application (client) ID
5. Create `outlook_credentials.json` at project root:
   ```json
   {"client_id": "<your-app-client-id>", "tenant_id": "consumers"}
   ```
