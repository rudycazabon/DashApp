"""Abstract base class that all DashApp tool plugins must implement."""

from abc import ABC, abstractmethod

from textual.widget import Widget


class BaseTool(ABC):
    """Interface every DashApp plugin must satisfy."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable tool name shown in the UI."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what the tool does."""

    @abstractmethod
    def build_widget(self) -> Widget:
        """Construct and return the Textual widget for this tool's tab."""
