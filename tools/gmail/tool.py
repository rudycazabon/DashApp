"""Gmail tool plugin — displays today's emails in a Textual DataTable."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable, Static

from tools.base import BaseTool
from tools.gmail.auth import get_credentials
from tools.gmail.client import fetch_todays_emails


class GmailWidget(Widget):
    """Textual widget that loads and displays today's Gmail messages."""

    def compose(self) -> ComposeResult:
        """Build the initial widget layout."""
        yield Static("Connecting to Gmail…", id="status")
        yield DataTable(id="table")

    def on_mount(self) -> None:
        """Kick off background data load when the widget is mounted."""
        self.run_worker(self._load, thread=True)

    def _load(self) -> None:
        """Fetch emails in a worker thread; update UI on the main thread."""
        try:
            creds = get_credentials()
            emails = fetch_todays_emails(creds)
            self.app.call_from_thread(self._populate, emails)  # type: ignore[attr-defined]
        except Exception as exc:
            self.app.call_from_thread(self._show_error, str(exc))  # type: ignore[attr-defined]

    def _populate(self, emails: list[dict[str, str]]) -> None:
        """Populate the DataTable with fetched emails."""
        table: DataTable = self.query_one("#table", DataTable)
        table.add_columns("Time", "From", "Subject", "Snippet")
        for email in emails:
            table.add_row(
                email["time"],
                email["from_"],
                email["subject"],
                email["snippet"],
            )
        count = len(emails)
        label = f"{count} message{'s' if count != 1 else ''} today"
        self.query_one("#status", Static).update(label)

    def _show_error(self, msg: str) -> None:
        """Display an error message in the status label."""
        self.query_one("#status", Static).update(f"[red]Error:[/red] {msg}")


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
