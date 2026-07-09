"""Confluence tool plugin — displays recent pages grouped by space."""

import logging

from rich.markup import escape
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Collapsible, Label, ProgressBar, Static

from tools.base import BaseTool
from tools.confluence.auth import get_auth
from tools.confluence.client import (
    fetch_pages,
    fetch_spaces,
    parse_page,
    parse_space,
)
from tools.widget import NavigableToolWidget

_log = logging.getLogger(__name__)


class ConfluenceWidget(NavigableToolWidget):
    """Textual widget that loads and displays recent Confluence pages by space."""

    DEFAULT_CSS = """
    ConfluenceWidget { height: 1fr; }
    ConfluenceWidget #status-bar {
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: tall $panel;
    }
    ConfluenceWidget #dot { width: 3; content-align: center middle; }
    ConfluenceWidget #status-text { width: 1fr; content-align: left middle; }
    ConfluenceWidget #progress { width: 30; }
    ConfluenceWidget #scroll { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        """Build the initial widget layout."""
        with Horizontal(id="status-bar"):
            yield Static("[red]●[/red]", id="dot")
            yield Static("Connecting to Confluence…", id="status-text")
            yield ProgressBar(total=100, show_eta=False, id="progress")
        with VerticalScroll(id="scroll"):
            yield Label("Loading…", id="placeholder")

    def on_mount(self) -> None:
        """Kick off background data load when the widget is mounted."""
        self.run_worker(self._load, thread=True)

    def _load(self) -> None:
        """Fetch spaces and pages in a worker thread; update UI on main thread."""

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
            self.app.call_from_thread(update_status, "Fetching spaces…")  # type: ignore[attr-defined]

            raw_spaces = fetch_spaces(session, base_url)
            spaces = [parse_space(s) for s in raw_spaces]
            _log.info("found %d spaces", len(spaces))
            self.app.call_from_thread(update_progress, 40)  # type: ignore[attr-defined]
            self.app.call_from_thread(update_status, "Fetching pages…")  # type: ignore[attr-defined]

            raw_pages = fetch_pages(session, base_url)
            pages = [parse_page(p) for p in raw_pages]
            _log.info("found %d recent pages across %d spaces", len(pages), len(spaces))
            self.app.call_from_thread(update_progress, 80)  # type: ignore[attr-defined]

            pages_by_space: dict[str, list[dict[str, str]]] = {}
            for page in pages:
                sid = page["space_id"]
                pages_by_space.setdefault(sid, []).append(page)

            self.app.call_from_thread(update_progress, 100)  # type: ignore[attr-defined]
            _log.info("load complete")
            self.app.call_from_thread(self._populate, spaces, pages_by_space)  # type: ignore[attr-defined]
        except Exception as exc:
            _log.error("load failed: %s", exc, exc_info=True)
            self.app.call_from_thread(self._show_error, str(exc))  # type: ignore[attr-defined]

    def _populate(
        self,
        spaces: list[dict[str, str]],
        pages_by_space: dict[str, list[dict[str, str]]],
    ) -> None:
        """Mount a Collapsible per space, each containing its recent pages."""
        try:
            self.query_one("#placeholder", Label).remove()
        except Exception:
            pass

        scroll = self.query_one("#scroll", VerticalScroll)
        total_pages = 0

        for space in spaces:
            space_id = space["id"]
            space_pages = pages_by_space.get(space_id, [])
            count = len(space_pages)
            total_pages += count
            space_title = f"{space['key']} — {space['name']} ({count} recent)"

            if not space_pages:
                inner: list[Widget] = [Label("No recent pages.", markup=False)]
            else:
                inner = []
                for page in space_pages:
                    page_title = f"{page['title'][:60]} [{page['status']}]"
                    body = (
                        f"Version: {page['version']}\nUpdated: {page['updated'][:10]}"
                    )
                    inner.append(
                        Collapsible(Label(body, markup=False), title=page_title)
                    )

            scroll.mount(Collapsible(Vertical(*inner), title=space_title))

        space_word = "space" if len(spaces) == 1 else "spaces"
        page_word = "page" if total_pages == 1 else "pages"
        label = f"{len(spaces)} {space_word}, {total_pages} recent {page_word}"
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
    """DashApp plugin that shows recent Confluence pages grouped by space."""

    @property
    def name(self) -> str:
        """Human-readable tool name."""
        return "Confluence"

    @property
    def description(self) -> str:
        """Short description of the tool."""
        return "Recently updated Confluence pages grouped by space"

    def build_widget(self) -> Widget:
        """Return the Confluence widget for the tab."""
        return ConfluenceWidget()
