"""Entry point for the DashApp TUI dashboard."""

import logging

from tui.app import DashApp


def main() -> None:
    """Configure logging and launch the application."""
    logging.basicConfig(level=logging.WARNING)
    DashApp().run()


if __name__ == "__main__":
    main()
