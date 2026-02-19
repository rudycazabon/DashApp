"""Entry point for the DashApp TUI dashboard."""

import logging

from tui.app import DashApp
from util.log import setup_logging

_log = logging.getLogger(__name__)


def main() -> None:
    """Configure logging and launch the application."""
    log_file = setup_logging()
    _log.info("DashApp starting — log: %s", log_file)
    try:
        DashApp().run()
        _log.info("DashApp session ended")
    except Exception:
        _log.critical("DashApp crashed", exc_info=True)
        raise


if __name__ == "__main__":
    main()
