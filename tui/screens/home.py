"""Home screen widget showing a welcome header and available tools."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Static

from tools.base import BaseTool


class HomeScreen(Widget):
    """Welcome widget listing all discovered tools.

    Args:
        tools: The list of loaded BaseTool instances.
    """

    DEFAULT_CSS = """
    HomeScreen {
        padding: 1 2;
    }
    HomeScreen .tool-entry {
        margin-top: 1;
    }
    """

    def __init__(self, tools: list[BaseTool]) -> None:
        super().__init__()
        self._tools = tools

    def compose(self) -> ComposeResult:
        """Render the welcome header and tool listing."""
        yield Static("[bold]Welcome to DashApp[/bold]", markup=True)
        yield Label("")
        if not self._tools:
            yield Label("No tools loaded.")
            return
        yield Label(f"[dim]{len(self._tools)} tool(s) available:[/dim]", markup=True)
        for tool in self._tools:
            yield Label(
                f"  [bold]{tool.name}[/bold] — {tool.description}",
                markup=True,
                classes="tool-entry",
            )
