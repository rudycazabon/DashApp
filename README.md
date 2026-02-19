# DashApp

A cross-platform, plugin-based TUI dashboard built with [Textual](https://textual.textualize.io/).

DashApp aggregates your personal productivity data — email, calendar — into a single
terminal interface. Each data source is a self-contained plugin discovered automatically
at startup.

---

## Screenshots

_Coming soon._

---

## Features

- **Tabbed interface** — Home tab lists all loaded tools; each tool gets its own tab
- **Plugin architecture** — drop a directory into `tools/` and it appears automatically
- **Persistent state** — SQLite database at `~/.dashapp/dashapp.db` stores config between sessions
- **Background loading** — each tool fetches data in a worker thread with a live progress bar
- **Collapsible entries** — click any row to expand full details

### Included tools

| Tool | What it shows |
|---|---|
| Gmail | Today's received messages |
| Google Calendar | Today's events from your primary calendar |
| Outlook | Today's received messages (personal Microsoft account) |
| Outlook Calendar | Today's events from your Outlook calendar |

---

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

---

## Installation

```bash
git clone <repo-url>
cd DashApp
uv sync
```

---

## Running

```bash
uv run dashapp
```

---

## Credentials setup

### Gmail and Google Calendar

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
2. Create an **OAuth 2.0 Client ID** (Desktop app type)
3. Enable the **Gmail API** and **Google Calendar API** for your project
4. Download the credentials file and save it as `credentials.json` in the project root
5. On first run, a browser window opens for OAuth consent; the token is cached at
   `~/.dashapp/gmail_token.json` and `~/.dashapp/calendar_token.json`

### Outlook Mail and Outlook Calendar

1. Go to [Azure Portal](https://portal.azure.com) → App registrations → New registration
2. Set **Supported account types** to "Personal Microsoft accounts only"
3. Add a **Redirect URI** → Platform: Mobile and desktop → URI: `http://localhost`
4. Copy the **Application (client) ID**
5. Create `outlook_credentials.json` in the project root:
   ```json
   {"client_id": "<your-app-client-id>", "tenant_id": "consumers"}
   ```
6. On first run, a browser window opens for OAuth consent; tokens are cached at
   `~/.dashapp/outlook_token.json` and `~/.dashapp/outlook_calendar_token.json`

Both credential files are gitignored and never committed.

---

## Project structure

```
DashApp/
├── main.py                       # Entry point
├── loader.py                     # Plugin discovery
├── config.py                     # Config wrapper (SQLite-backed key-value store)
├── tui/
│   ├── app.py                    # DashApp — TabbedContent shell
│   └── screens/home.py           # Home tab widget
├── tools/
│   ├── base.py                   # BaseTool ABC
│   ├── gmail/                    # Gmail tool
│   ├── calendar/                 # Google Calendar tool
│   ├── outlook/                  # Outlook mail tool
│   └── outlook_calendar/         # Outlook Calendar tool
├── db/manager.py                 # SQLite helpers
├── util/paths.py                 # Shared filesystem paths
└── tests/                        # pytest suite (68 tests)
```

---

## Adding a new tool

1. Create `tools/<toolname>/`
2. Add `manifest.json`:
   ```json
   {"name": "My Tool", "version": "0.1.0", "description": "What it does", "author": "You"}
   ```
3. Add `tool.py`:
   ```python
   from textual.widget import Widget
   from tools.base import BaseTool

   class MyWidget(Widget):
       def compose(self): ...

   class Tool(BaseTool):
       @property
       def name(self) -> str: return "My Tool"

       @property
       def description(self) -> str: return "What it does"

       def build_widget(self) -> Widget: return MyWidget()
   ```
4. Restart DashApp — the new tab appears automatically.

---

## Development

```bash
# Format
uv run ruff format .

# Lint
uv run ruff check . --fix

# Type check
uv run pyright

# Tests
uv run pytest tests/ -v
```

Pre-commit hooks (ruff + prettier) run automatically on `git commit`.

---

## Roadmap

- [ ] Packaging and cross-platform deployment testing (Linux, macOS)
- [ ] Mobile client
- [ ] Web client
