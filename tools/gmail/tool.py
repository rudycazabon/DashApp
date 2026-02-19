"""Gmail tool plugin — displays today's emails as expandable Collapsible entries."""

import logging
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Collapsible, Label, ProgressBar, Static

from tools.base import BaseTool
from tools.gmail.auth import get_credentials
from tools.gmail.client import fetch_message_detail, fetch_message_ids, get_service

_log = logging.getLogger(__name__)


class GmailWidget(Widget):
    """Textual widget that loads and displays today's Gmail messages."""

    DEFAULT_CSS = """
    GmailWidget { height: 1fr; }
    GmailWidget #status-bar {
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: tall $panel;
    }
    GmailWidget #dot { width: 3; content-align: center middle; }
    GmailWidget #status-text { width: 1fr; content-align: left middle; }
    GmailWidget #progress { width: 30; }
    GmailWidget #scroll { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        """Build the initial widget layout."""
        with Horizontal(id="status-bar"):
            yield Static("[red]●[/red]", id="dot")
            yield Static("Connecting to Gmail…", id="status-text")
            yield ProgressBar(total=100, show_eta=False, id="progress")
        with VerticalScroll(id="scroll"):
            yield Label("Loading…", id="placeholder")

    def on_mount(self) -> None:
        """Kick off background data load when the widget is mounted."""
        self.run_worker(self._load, thread=True)

    def _load(self) -> None:
        """Fetch emails in a worker thread; update UI on the main thread."""

        def update_progress(value: int) -> None:
            self.query_one("#progress", ProgressBar).progress = value

        def update_status(text: str) -> None:
            self.query_one("#status-text", Static).update(text)

        _log.info("loading started")
        try:
            self.app.call_from_thread(update_progress, 0)  # type: ignore[attr-defined]

            creds = get_credentials()
            _log.info("auth successful")
            self.app.call_from_thread(update_progress, 20)  # type: ignore[attr-defined]
            self.app.call_from_thread(update_status, "Fetching message list…")  # type: ignore[attr-defined]

            service = get_service(creds)
            today = datetime.now().strftime("%Y/%m/%d")
            stubs = fetch_message_ids(service, today)
            _log.info("found %d message stubs", len(stubs))
            self.app.call_from_thread(update_progress, 40)  # type: ignore[attr-defined]

            total = len(stubs)
            emails: list[dict[str, str]] = []
            for i, stub in enumerate(stubs):
                detail = fetch_message_detail(service, stub["id"])
                emails.append(detail)
                pct = 40 + int(60 * (i + 1) / max(total, 1))
                self.app.call_from_thread(update_progress, pct)  # type: ignore[attr-defined]

            _log.info("loaded %d emails", len(emails))
            self.app.call_from_thread(self._populate, emails)  # type: ignore[attr-defined]
        except Exception as exc:
            _log.error("load failed: %s", exc, exc_info=True)
            self.app.call_from_thread(self._show_error, str(exc))  # type: ignore[attr-defined]

    def _populate(self, emails: list[dict[str, str]]) -> None:
        """Mount Collapsible entries for each email; update status and hide progress."""
        try:
            self.query_one("#placeholder", Label).remove()
        except Exception:
            pass

        scroll = self.query_one("#scroll", VerticalScroll)
        for email in emails:
            subject = email["subject"][:50]
            from_ = email["from_"][:30]
            title = f"{subject} — {from_}"
            body = (
                f"From:    {email['from_']}\n"
                f"Date:    {email['time']}\n"
                f"Snippet: {email['snippet']}"
            )
            scroll.mount(Collapsible(Label(body, markup=False), title=title))

        count = len(emails)
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
    """DashApp plugin that shows today's Gmail messages."""

    @property
    def name(self) -> str:
        """Human-readable tool name."""
        return "Gmail"

    @property
    def description(self) -> str:
        """Short description of the tool."""
        return "Today's Gmail messages"

    def build_widget(self) -> Widget:
        """Return the Gmail widget for the tab."""
        return GmailWidget()
