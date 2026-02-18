"""DashApp — main Textual application."""

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane

from loader import load_tools
from tools.base import BaseTool
from tui.screens.home import HomeScreen


class DashApp(App[None]):
    """Top-level Textual application with a tab per loaded tool."""

    TITLE = "DashApp"
    SUB_TITLE = "Your personal TUI dashboard"

    def __init__(self) -> None:
        super().__init__()
        self._tools: list[BaseTool] = load_tools()

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
