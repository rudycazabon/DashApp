"""Shared navigable base widget for tool plugins."""

from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Collapsible


class NavigableToolWidget(Widget):
    """Base widget providing Up/Down/Left/Right keyboard navigation for Collapsibles.

    - Up/Down: move focus between top-level Collapsible items in the scroll area.
    - Left/Right: collapse/expand the currently focused Collapsible.

    Priority bindings ensure these intercept VerticalScroll's default scroll
    behaviour so arrow keys navigate items rather than scroll the container.
    """

    BINDINGS = [
        Binding("up", "focus_prev_item", "Prev item", priority=True, show=False),
        Binding("down", "focus_next_item", "Next item", priority=True, show=False),
        Binding("left", "collapse_item", "Collapse", priority=True, show=False),
        Binding("right", "expand_item", "Expand", priority=True, show=False),
    ]

    def _top_level_collapsibles(self) -> list[Collapsible]:
        """Return direct Collapsible children of the #scroll container."""
        try:
            scroll = self.query_one("#scroll", VerticalScroll)
        except Exception:
            return []
        return [c for c in scroll.children if isinstance(c, Collapsible)]

    def action_focus_prev_item(self) -> None:
        """Move focus to the previous top-level Collapsible, wrapping around."""
        items = self._top_level_collapsibles()
        if not items:
            return
        focused = self.app.focused
        if isinstance(focused, Collapsible) and focused in items:
            idx = items.index(focused)
            items[(idx - 1) % len(items)].focus()
        else:
            items[0].focus()

    def action_focus_next_item(self) -> None:
        """Move focus to the next top-level Collapsible, wrapping around."""
        items = self._top_level_collapsibles()
        if not items:
            return
        focused = self.app.focused
        if isinstance(focused, Collapsible) and focused in items:
            idx = items.index(focused)
            items[(idx + 1) % len(items)].focus()
        else:
            items[0].focus()

    def action_collapse_item(self) -> None:
        """Collapse the currently focused Collapsible."""
        focused = self.app.focused
        if isinstance(focused, Collapsible):
            focused.collapsed = True

    def action_expand_item(self) -> None:
        """Expand the currently focused Collapsible."""
        focused = self.app.focused
        if isinstance(focused, Collapsible):
            focused.collapsed = False
