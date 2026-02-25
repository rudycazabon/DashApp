"""DashApp — main Textual application."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, TabbedContent, TabPane

from loader import load_tools
from tools.base import BaseTool
from tui.screens.home import HomeScreen


class DashApp(App[None]):
    """Top-level Textual application with a tab per loaded tool."""

    TITLE = "DashApp"
    SUB_TITLE = "Your personal TUI dashboard"

    BINDINGS = [
        Binding("tab", "next_tab", "Next Tab", priority=True, show=True),
        Binding("shift+tab", "prev_tab", "Prev Tab", priority=True, show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._tools: list[BaseTool] = load_tools()

    def action_next_tab(self) -> None:
        """Switch to the next tab."""
        self.query_one(TabbedContent).action_next_tab()  # type: ignore[attr-defined]

    def action_prev_tab(self) -> None:
        """Switch to the previous tab."""
        self.query_one(TabbedContent).action_previous_tab()  # type: ignore[attr-defined]

    def compose(self) -> ComposeResult:
        """Build the full UI: header, tabbed content, footer."""
        yield Header()
        with TabbedContent(initial="home"):
            with TabPane("Home", id="home"):
                yield HomeScreen(self._tools)
            for tool in self._tools:
                tab_id = tool.name.lower().replace(" ", "-")
                with TabPane(tool.name, id=tab_id):
                    yield tool.build_widget()
        yield Footer()
