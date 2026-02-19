"""Jira tool plugin — displays open issues grouped by project."""

import logging

from rich.markup import escape
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Collapsible, Label, ProgressBar, Static

from tools.base import BaseTool
from tools.jira.auth import get_auth
from tools.jira.client import fetch_issues, fetch_projects, parse_issue, parse_project

_log = logging.getLogger(__name__)


class JiraWidget(Widget):
    """Textual widget that loads and displays open Jira issues by project."""

    DEFAULT_CSS = """
    JiraWidget { height: 1fr; }
    JiraWidget #status-bar {
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: tall $panel;
    }
    JiraWidget #dot { width: 3; content-align: center middle; }
    JiraWidget #status-text { width: 1fr; content-align: left middle; }
    JiraWidget #progress { width: 30; }
    JiraWidget #scroll { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        """Build the initial widget layout."""
        with Horizontal(id="status-bar"):
            yield Static("[red]●[/red]", id="dot")
            yield Static("Connecting to Jira…", id="status-text")
            yield ProgressBar(total=100, show_eta=False, id="progress")
        with VerticalScroll(id="scroll"):
            yield Label("Loading…", id="placeholder")

    def on_mount(self) -> None:
        """Kick off background data load when the widget is mounted."""
        self.run_worker(self._load, thread=True)

    def _load(self) -> None:
        """Fetch projects and issues in a worker thread; update UI on main thread."""

        def update_progress(value: int) -> None:
            self.query_one("#progress", ProgressBar).progress = value

        def update_status(text: str) -> None:
            self.query_one("#status-text", Static).update(text)

        _log.info("loading started")
        try:
            self.app.call_from_thread(update_progress, 0)  # type: ignore[attr-defined]

            session, base_url = get_auth()
            _log.info("auth successful — %s", base_url)
            self.app.call_from_thread(update_progress, 20)  # type: ignore[attr-defined]
            self.app.call_from_thread(update_status, "Fetching projects…")  # type: ignore[attr-defined]

            raw_projects = fetch_projects(session, base_url)
            projects = [parse_project(p) for p in raw_projects]
            _log.info("found %d projects", len(projects))
            self.app.call_from_thread(update_progress, 40)  # type: ignore[attr-defined]
            self.app.call_from_thread(update_status, "Fetching issues…")  # type: ignore[attr-defined]

            project_keys = [p["key"] for p in projects]
            raw_issues = fetch_issues(session, base_url, project_keys)
            issues = [parse_issue(i) for i in raw_issues]
            _log.info(
                "found %d open issues across %d projects", len(issues), len(projects)
            )
            self.app.call_from_thread(update_progress, 80)  # type: ignore[attr-defined]

            issues_by_project: dict[str, list[dict[str, str]]] = {}
            for issue in issues:
                pk = issue["project_key"]
                issues_by_project.setdefault(pk, []).append(issue)

            self.app.call_from_thread(update_progress, 100)  # type: ignore[attr-defined]
            _log.info("load complete")
            self.app.call_from_thread(self._populate, projects, issues_by_project)  # type: ignore[attr-defined]
        except Exception as exc:
            _log.error("load failed: %s", exc, exc_info=True)
            self.app.call_from_thread(self._show_error, str(exc))  # type: ignore[attr-defined]

    def _populate(
        self,
        projects: list[dict[str, str]],
        issues_by_project: dict[str, list[dict[str, str]]],
    ) -> None:
        """Mount a Collapsible per project, each containing its open issues."""
        try:
            self.query_one("#placeholder", Label).remove()
        except Exception:
            pass

        scroll = self.query_one("#scroll", VerticalScroll)
        total_issues = 0

        for project in projects:
            key = project["key"]
            proj_issues = issues_by_project.get(key, [])
            count = len(proj_issues)
            total_issues += count
            proj_title = f"{key} — {project['name']} ({count} open)"

            if not proj_issues:
                inner: list[Widget] = [Label("No open issues.", markup=False)]
            else:
                inner = []
                for issue in proj_issues:
                    issue_title = (
                        f"{issue['key']} — {issue['summary'][:50]} [{issue['status']}]"
                    )
                    body = (
                        f"Type:     {issue['type']}\n"
                        f"Priority: {issue['priority']}\n"
                        f"Assignee: {issue['assignee']}\n"
                        f"Updated:  {issue['updated'][:10]}"
                    )
                    inner.append(
                        Collapsible(Label(body, markup=False), title=issue_title)
                    )

            scroll.mount(Collapsible(Vertical(*inner), title=proj_title))

        proj_word = "project" if len(projects) == 1 else "projects"
        issue_word = "issue" if total_issues == 1 else "issues"
        label = f"{len(projects)} {proj_word}, {total_issues} open {issue_word}"
        self.query_one("#status-text", Static).update(label)
        self.query_one("#dot", Static).update("[green]●[/green]")
        self.query_one("#progress", ProgressBar).display = False

    def _show_error(self, msg: str) -> None:
        """Display an error message; update dot to red and hide progress."""
        try:
            self.query_one("#placeholder", Label).remove()
        except Exception:
            pass

        self.query_one("#dot", Static).update("[red]●[/red]")
        self.query_one("#status-text", Static).update(
            f"[red]Error:[/red] {escape(msg)}"
        )
        self.query_one("#progress", ProgressBar).display = False


class Tool(BaseTool):
    """DashApp plugin that shows open Jira issues grouped by project."""

    @property
    def name(self) -> str:
        """Human-readable tool name."""
        return "Jira"

    @property
    def description(self) -> str:
        """Short description of the tool."""
        return "Open Jira issues grouped by project"

    def build_widget(self) -> Widget:
        """Return the Jira widget for the tab."""
        return JiraWidget()
