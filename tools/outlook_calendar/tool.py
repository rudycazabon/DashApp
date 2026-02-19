"""Outlook Calendar tool plugin — displays today's personal calendar events."""

import logging

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Collapsible, Label, ProgressBar, Static

from tools.base import BaseTool
from tools.outlook_calendar.auth import get_access_token
from tools.outlook_calendar.client import (
    _today_bounds_utc,
    fetch_events,
    parse_event,
)

_log = logging.getLogger(__name__)


class OutlookCalendarWidget(Widget):
    """Textual widget that loads and displays today's Outlook Calendar events."""

    DEFAULT_CSS = """
    OutlookCalendarWidget { height: 1fr; }
    OutlookCalendarWidget #status-bar {
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: tall $panel;
    }
    OutlookCalendarWidget #dot { width: 3; content-align: center middle; }
    OutlookCalendarWidget #status-text { width: 1fr; content-align: left middle; }
    OutlookCalendarWidget #progress { width: 30; }
    OutlookCalendarWidget #scroll { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        """Build the initial widget layout."""
        with Horizontal(id="status-bar"):
            yield Static("[red]●[/red]", id="dot")
            yield Static("Connecting to Outlook Calendar…", id="status-text")
            yield ProgressBar(total=100, show_eta=False, id="progress")
        with VerticalScroll(id="scroll"):
            yield Label("Loading…", id="placeholder")

    def on_mount(self) -> None:
        """Kick off background data load when the widget is mounted."""
        self.run_worker(self._load, thread=True)

    def _load(self) -> None:
        """Fetch events in a worker thread; update UI on the main thread."""

        def update_progress(value: int) -> None:
            self.query_one("#progress", ProgressBar).progress = value

        def update_status(text: str) -> None:
            self.query_one("#status-text", Static).update(text)

        _log.info("loading started")
        try:
            self.app.call_from_thread(update_progress, 0)  # type: ignore[attr-defined]

            token = get_access_token()
            _log.info("auth successful")
            self.app.call_from_thread(update_progress, 20)  # type: ignore[attr-defined]
            self.app.call_from_thread(update_status, "Fetching events…")  # type: ignore[attr-defined]

            time_min, time_max = _today_bounds_utc()
            self.app.call_from_thread(update_progress, 40)  # type: ignore[attr-defined]

            stubs = fetch_events(token, time_min, time_max)
            _log.info("found %d events", len(stubs))
            self.app.call_from_thread(update_progress, 80)  # type: ignore[attr-defined]

            events = [parse_event(s) for s in stubs]
            self.app.call_from_thread(update_progress, 100)  # type: ignore[attr-defined]

            _log.info("loaded %d events", len(events))
            self.app.call_from_thread(self._populate, events)  # type: ignore[attr-defined]
        except Exception as exc:
            _log.error("load failed: %s", exc, exc_info=True)
            self.app.call_from_thread(self._show_error, str(exc))  # type: ignore[attr-defined]

    def _populate(self, events: list[dict[str, str]]) -> None:
        """Mount Collapsible entries for each event; update status."""
        try:
            self.query_one("#placeholder", Label).remove()
        except Exception:
            pass

        scroll = self.query_one("#scroll", VerticalScroll)
        for event in events:
            start = event["start"]
            if event["is_all_day"] == "True":
                start_fmt = "All day"
            elif "T" in start:
                # dateTime format: 2026-02-19T09:00:00.0000000 → 09:00
                start_fmt = start[11:16]
            else:
                start_fmt = "All day"

            summary = event["summary"][:50]
            title = f"{start_fmt} — {summary}"
            body = (
                f"Start:    {event['start']}\n"
                f"End:      {event['end']}\n"
                f"Location: {event['location']}\n"
                f"Notes:    {event['description'][:200]}"
            )
            scroll.mount(Collapsible(Label(body, markup=False), title=title))

        count = len(events)
        label = f"{count} event{'s' if count != 1 else ''} today"
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
        self.query_one("#status-text", Static).update(f"[red]Error:[/red] {msg}")
        self.query_one("#progress", ProgressBar).display = False


class Tool(BaseTool):
    """DashApp plugin that shows today's personal Outlook Calendar events."""

    @property
    def name(self) -> str:
        """Human-readable tool name."""
        return "Outlook Calendar"

    @property
    def description(self) -> str:
        """Short description of the tool."""
        return "Today's personal Outlook calendar events"

    def build_widget(self) -> Widget:
        """Return the Outlook Calendar widget for the tab."""
        return OutlookCalendarWidget()
