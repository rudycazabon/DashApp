"""Demo tool plugin — proof-of-concept for the DashApp plugin system."""

from textual.widget import Widget
from textual.widgets import Static

from tools.base import BaseTool


class Tool(BaseTool):
    """A minimal demo tool that renders a greeting widget."""

    @property
    def name(self) -> str:
        """Human-readable tool name."""
        return "Demo"

    @property
    def description(self) -> str:
        """Short description of the tool."""
        return "Proof-of-concept plugin demonstrating the DashApp plugin system"

    def build_widget(self) -> Widget:
        """Return a simple static greeting widget."""
        return Static("Hello from DashApp!")
