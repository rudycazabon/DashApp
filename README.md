# DashApp

A cross-platform, plugin-based TUI dashboard built with [Textual](https://textual.textualize.io/).

DashApp aggregates your personal productivity data into a single terminal interface.
Each data source is a self-contained plugin discovered automatically at startup.

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
| Jira | Open issues grouped by project |
| Confluence | Recently updated pages grouped by space |

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

### Jira and Confluence

Both use an Atlassian API token (same token works for both).

1. Create an **API token** at
   [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create `~/.dashapp/jira_credentials.json`:
   ```json
   {"url": "https://yourco.atlassian.net", "email": "you@example.com", "api_token": "<your-api-token>"}
   ```
3. Create `~/.dashapp/confluence_credentials.json` (same site URL, email, and token):
   ```json
   {"url": "https://yourco.atlassian.net", "email": "you@example.com", "api_token": "<your-api-token>"}
   ```

All credential files live in `~/.dashapp/` — never in the project root.

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
│   ├── demo/                     # Smoke-test plugin
│   ├── jira/                     # Jira tool
│   └── confluence/               # Confluence tool
├── db/manager.py                 # SQLite helpers
├── util/paths.py                 # Shared filesystem paths
└── tests/                        # pytest suite (57 tests)
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
