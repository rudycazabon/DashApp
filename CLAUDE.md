# Project Description

The goal of this project is to create a cross-platform (Linux, Windows, and MacOS) Python textual UI (TUI) dashboard application that shall be named "DashApp." DashApp will be developed in stages. At its core, DashApp will be a plugin based such that each new tool will be added as python plugins. Throughout the development of new tools, bug fixing, packaging, and deployment cycle testing will be performed. Initially this application will be geared towards deployment on the desktop. Later, a mobile and web-client will be developed.

# Development Guidelines

This document contains critical information about working with this codebase. Follow these guidelines precisely.

## Core Development Rules

1. Package Management
   - ONLY use uv, NEVER pip
   - Installation: `uv add package`
   - Running tools: `uv run tool`
   - Upgrading: `uv add --dev package --upgrade-package package`
   - FORBIDDEN: `uv pip install`, `@latest` syntax

2. Code Quality
   - Type hints required for all code
   - Public APIs must have docstrings
   - Functions must be focused and small
   - Follow existing patterns exactly
   - Line length: 88 chars maximum

3. Testing Requirements
   - Framework: `uv run pytest`
   - Async testing: use anyio, not asyncio
   - Coverage: test edge cases and errors
   - New features require tests
   - Bug fixes require regression tests

4. Code Style
    - PEP 8 naming (snake_case for functions/variables)
    - Class names in PascalCase
    - Constants in UPPER_SNAKE_CASE
    - Document with docstrings
    - Use f-strings for formatting

## Development Philosophy

- **Simplicity**: Write simple, straightforward code
- **Readability**: Make code easy to understand
- **Performance**: Consider performance without sacrificing readability
- **Maintainability**: Write code that's easy to update
- **Testability**: Ensure code is testable
- **Reusability**: Create reusable components and functions
- **Less Code = Less Debt**: Minimize code footprint

## Coding Best Practices

- **Early Returns**: Use to avoid nested conditions
- **Descriptive Names**: Use clear variable/function names (prefix handlers with "handle")
- **Constants Over Functions**: Use constants where possible
- **DRY Code**: Don't repeat yourself
- **Functional Style**: Prefer functional, immutable approaches when not verbose
- **Minimal Changes**: Only modify code related to the task at hand
- **Function Ordering**: Define composing functions before their components
- **TODO Comments**: Mark issues in existing code with "TODO:" prefix
- **Simplicity**: Prioritize simplicity and readability over clever solutions
- **Build Iteratively** Start with minimal functionality and verify it works before adding complexity
- **Run Tests**: Test your code frequently with realistic inputs and validate outputs
- **Build Test Environments**: Create testing environments for components that are difficult to validate directly
- **Functional Code**: Use functional and stateless approaches where they improve clarity
- **Clean logic**: Keep core logic clean and push implementation details to the edges
- **File Organisation**: Balance file organization with simplicity - use an appropriate number of files for the project scale

# Project Structure

```
DashApp/
├── main.py                       # Entry point — launches DashApp().run()
├── loader.py                     # Plugin discovery and loading
├── config.py                     # Config class — high-level get/set over SQLite
├── pyproject.toml                # Dependencies and uv script entry point
├── tui/
│   ├── app.py                    # DashApp(App[None]) — TabbedContent shell
│   └── screens/
│       └── home.py               # HomeScreen widget — lists loaded tools
├── tools/                        # Plugin directory — one sub-package per tool
│   ├── base.py                   # BaseTool ABC (name, description, build_widget)
│   ├── demo/                     # Smoke-test plugin
│   ├── gmail/                    # Gmail mail tool
│   ├── calendar/                 # Google Calendar tool
│   ├── outlook/                  # Outlook mail tool
│   └── outlook_calendar/         # Outlook Calendar tool
├── db/
│   └── manager.py                # SQLite helpers (get_connection, get/set_setting)
├── util/
│   └── paths.py                  # APP_DIR, DB_PATH, LOGS_DIR constants
└── tests/                        # pytest test suite
```

# System Architecture

## Entry point

`main.py` configures logging then calls `DashApp().run()`. The `dashapp` script in
`pyproject.toml` points here. Run with `uv run python main.py` or (after `uv sync`)
`uv run dashapp`.

## TUI (`tui/`)

`tui/app.py` — `DashApp(App[None])`:
- Calls `load_tools()` at init to discover plugins.
- `compose()` builds a `TabbedContent` with a fixed `Home` tab followed by one
  `TabPane` per loaded tool. Tab IDs are `tool.name.lower().replace(" ", "-")`.
- `Header` and `Footer` wrap the content.

`tui/screens/home.py` — `HomeScreen(Widget)`:
- Receives the tool list and renders a welcome header plus a labelled entry for each
  tool showing its name and description.

## Plugin system (`loader.py`, `tools/`)

`loader.py` — `load_tools() -> list[BaseTool]`:
- Iterates `tools/` sorted alphabetically, skipping `_`-prefixed directories.
- For each candidate, requires `manifest.json` (must have a `"name"` key) and `tool.py`.
- Imports `tools.<dir>.tool` and instantiates the `Tool` class (must subclass `BaseTool`).
- Errors are logged as warnings and the plugin is skipped; the app always starts.

`tools/base.py` — `BaseTool(ABC)`:
- Three abstract members every plugin must implement:
  - `name: str` — shown in tabs and the home screen.
  - `description: str` — shown on the home screen.
  - `build_widget() -> Widget` — returns the Textual widget for the tab pane.

`tools/<name>/manifest.json` — plugin metadata:
```json
{"name": "Tool Name", "version": "0.1.0", "description": "...", "author": "DashApp"}
```

`tools/<name>/tool.py` — plugin implementation:
- Must define `class Tool(BaseTool)` implementing the three abstract members.
- Widget classes follow the pattern: status bar (dot + text + progress bar) +
  `VerticalScroll` of `Collapsible` entries. Data loaded in a worker thread via
  `self.run_worker(self._load, thread=True)`. UI updates from the worker use
  `self.app.call_from_thread(...)`.

## Database (`db/`, `config.py`)

`db/manager.py`:
- `get_connection(db_path)` — opens/creates `~/.dashapp/dashapp.db`, creates the
  `settings` table if absent, sets `row_factory`.
- `get_setting(key, conn)` / `set_setting(key, value, conn)` — key-value store backed
  by a single `settings` table with upsert.

`config.py` — `Config` class:
- Thin wrapper holding an open connection; exposes `get(key, default)`, `set(key, value)`,
  `close()`.

`util/paths.py`:
- `APP_DIR = Path.home() / ".dashapp"`
- `DB_PATH = APP_DIR / "dashapp.db"`
- `LOGS_DIR = APP_DIR / "logs"`

## Implemented tools

| Tool | Package | API | Credentials |
|---|---|---|---|
| Gmail | `tools/gmail/` | Gmail API v1 | `credentials.json` (Google Cloud) |
| Google Calendar | `tools/calendar/` | Calendar API v3 | `credentials.json` (same file) |
| Outlook Mail | `tools/outlook/` | Graph `/me/messages` | `outlook_credentials.json` |
| Outlook Calendar | `tools/outlook_calendar/` | Graph `/me/calendarView` | `outlook_credentials.json` (same file) |

Each tool has three files: `auth.py` (token acquisition + cache), `client.py` (pure API
functions), `tool.py` (widget + `Tool` class).

Google tools use `google-auth-oauthlib` (`InstalledAppFlow`). Token files:
`~/.dashapp/gmail_token.json`, `~/.dashapp/calendar_token.json`.

Outlook tools use `msal.PublicClientApplication` (no client secret; personal accounts).
Token files: `~/.dashapp/outlook_token.json`, `~/.dashapp/outlook_calendar_token.json`.
`outlook_credentials.json` format: `{"client_id": "...", "tenant_id": "consumers"}`.

## Pull Requests

- Create a detailed message of what changed. Focus on the high level description of
  the problem it tries to solve, and how it is solved. Don't go into the specifics of the
  code unless it adds clarity.

## Code Formatting

1. Ruff
   - Format: `uv run ruff format .`
   - Check: `uv run ruff check .`
   - Fix: `uv run ruff check . --fix`
   - Critical issues:
     - Line length (88 chars)
     - Import sorting (I001)
     - Unused imports
   - Line wrapping:
     - Strings: use parentheses
     - Function calls: multi-line with proper indent
     - Imports: split into multiple lines

2. Type Checking
   - Tool: `uv run pyright`
   - Requirements:
     - Explicit None checks for Optional
     - Type narrowing for strings
     - Version warnings can be ignored if checks pass

3. Pre-commit
   - Config: `.pre-commit-config.yaml`
   - Runs: on git commit
   - Tools: Prettier (YAML/JSON), Ruff (Python)
   - Ruff updates:
     - Check PyPI versions
     - Update config rev
     - Commit config first

## Error Resolution

1. Common Issues
   - Line length:
     - Break strings with parentheses
     - Multi-line function calls
     - Split imports
   - Types:
     - Add None checks
     - Narrow string types
     - Match existing patterns

2. Best Practices
   - Check git status before commits
   - Run formatters before type checks
   - Keep changes minimal
   - Follow existing patterns
   - Document public APIs
   - Test thoroughly
