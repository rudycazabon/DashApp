# DashApp TODO

> Auto-maintained per CLAUDE.md directive. Update on every session start if tasks change.
> Last updated: 2026-02-25

---

## Pending Tasks

### 1. Create TODO.md (this file)
- **Status:** Done
- **Context:** CLAUDE.md global directive requires a TODO.md listing all tasks.

---

### 2. Cross-platform testing
- **Status:** Pending
- **Context:** App developed on Windows. Must verify on Linux and macOS:
  - `~/.dashapp/` path resolution via `Path.home()` (should work, but untested)
  - Textual rendering differences (terminal emulators, color support)
  - `uv run dashapp` entry point works on all platforms
  - No Windows-specific path separators leaked into code
- **How to test:** Run `uv run dashapp` on Linux/macOS; exercise each tab.

---

### 3. Packaging and distribution
- **Status:** Pending
- **Context:** `pyproject.toml` already has a `[project.scripts]` entry (`dashapp`).
  Need to verify wheel build, standalone install, and `uv tool install` workflow.
- **Steps:**
  - `uv build` — produce sdist + wheel in `dist/`
  - `uv tool install dist/dashapp-*.whl` — test isolated install
  - Verify `dashapp` command works after install without dev dependencies
  - Consider adding a `MANIFEST.in` or `[tool.hatch.build]` include rules if
    `tools/` plugin manifests are not bundled automatically

---

### 4. Home tab content
- **Status:** Pending
- **Context:** `tui/screens/home.py` renders a static welcome header + tool list.
  Could be enhanced to show live status (last-loaded counts, auth state) or
  quick-nav links. Low priority; cosmetic improvement only.
- **File:** `tui/screens/home.py`

---

### 5. Additional tool plugins
- **Status:** Pending (no specific tool chosen yet)
- **Context:** Plugin system is stable. Each new tool follows the pattern:
  `tools/<name>/{__init__.py, manifest.json, auth.py, client.py, tool.py}`
  and adds ~14-16 tests. Candidate tools: GitHub Issues, Slack, Linear, PagerDuty.
- **To start:** Pick a tool, confirm API/auth approach, follow existing plugin patterns.

---

### 6. Test coverage audit
- **Status:** Pending
- **Context:** Suite is 90 tests covering auth, client, and path logic per tool.
  No widget/integration tests yet. Consider adding smoke tests for `load_tools()`
  and `DashApp` composition using Textual's `Pilot` test API.
- **How to run:** `uv run pytest tests/ -v --tb=short`

---

## Completed Tasks (archive)

| # | Task | Checkpoint |
|---|---|---|
| C01 | Core scaffold (TUI shell, plugin loader, DB, config) | `checkpoints/01-core-scaffold.md` |
| C02 | Gmail tool | `checkpoints/02-gmail-tool.md` |
| C03 | Google Calendar tool | `checkpoints/03-calendar-tool.md` |
| C04 | Outlook Mail tool | `checkpoints/04-outlook-tool.md` |
| C05 | Outlook Calendar tool | `checkpoints/05-outlook-calendar-tool.md` |
| C06 | Jira tool + session logging | `checkpoints/08-jira-tool-and-logging.md` |
| C07 | Credential migration to `~/.dashapp/` | `checkpoints/09-credential-migration.md` |
