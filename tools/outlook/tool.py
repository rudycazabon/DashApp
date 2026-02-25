"""Outlook tool plugin — displays today's personal Outlook messages."""

import logging

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Collapsible, Label, ProgressBar, Static

from tools.base import BaseTool
from tools.outlook.auth import get_access_token
from tools.outlook.client import fetch_todays_messages
from tools.widget import NavigableToolWidget

_log = logging.getLogger(__name__)


class OutlookWidget(NavigableToolWidget):
    """Textual widget that loads and displays today's Outlook messages."""

    DEFAULT_CSS = """
    OutlookWidget { height: 1fr; }
    OutlookWidget #status-bar {
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: tall $panel;
    }
    OutlookWidget #dot { width: 3; content-align: center middle; }
    OutlookWidget #status-text { width: 1fr; content-align: left middle; }
    OutlookWidget #progress { width: 30; }
    OutlookWidget #scroll { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        """Build the initial widget layout."""
        with Horizontal(id="status-bar"):
            yield Static("[red]●[/red]", id="dot")
            yield Static("Connecting to Outlook…", id="status-text")
            yield ProgressBar(total=100, show_eta=False, id="progress")
        with VerticalScroll(id="scroll"):
            yield Label("Loading…", id="placeholder")

    def on_mount(self) -> None:
        """Kick off background data load when the widget is mounted."""
        self.run_worker(self._load, thread=True)

    def _load(self) -> None:
        """Fetch messages in a worker thread; update UI on the main thread."""

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
            self.app.call_from_thread(update_status, "Fetching messages…")  # type: ignore[attr-defined]

            self.app.call_from_thread(update_progress, 40)  # type: ignore[attr-defined]
            messages = fetch_todays_messages(token)
            _log.info("loaded %d messages", len(messages))
            self.app.call_from_thread(update_progress, 80)  # type: ignore[attr-defined]

            self.app.call_from_thread(self._populate, messages)  # type: ignore[attr-defined]
        except Exception as exc:
            _log.error("load failed: %s", exc, exc_info=True)
            self.app.call_from_thread(self._show_error, str(exc))  # type: ignore[attr-defined]

    def _populate(self, messages: list[dict[str, str]]) -> None:
        """Mount Collapsible entries for each message; update status."""
        try:
            self.query_one("#placeholder", Label).remove()
        except Exception:
            pass

        scroll = self.query_one("#scroll", VerticalScroll)
        for msg in messages:
            subject = msg["subject"][:50]
            from_ = msg["from_"][:30]
            title = f"{subject} — {from_}"
            body = (
                f"From:    {msg['from_']}\n"
                f"Date:    {msg['time']}\n"
                f"Snippet: {msg['snippet']}"
            )
            scroll.mount(Collapsible(Label(body, markup=False), title=title))

        count = len(messages)
        label = f"{count} message{'s' if count != 1 else ''} today"
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
    """DashApp plugin that shows today's personal Outlook messages."""

    @property
    def name(self) -> str:
        """Human-readable tool name."""
        return "Outlook"

    @property
    def description(self) -> str:
        """Short description of the tool."""
        return "Today's personal Outlook messages"

    def build_widget(self) -> Widget:
        """Return the Outlook widget for the tab."""
        return OutlookWidget()
