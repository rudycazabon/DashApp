"""Session logging setup for DashApp."""

import logging
from datetime import datetime
from pathlib import Path

from util.paths import LOGS_DIR

_LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)s - %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(logs_dir: Path = LOGS_DIR) -> Path:
    """Configure file logging for this session.

    Creates a timestamped log file in *logs_dir* and attaches a
    ``FileHandler`` to the root logger at ``INFO`` level.

    Args:
        logs_dir: Directory in which to create the log file.
                  Defaults to ``~/.dashapp/logs/``.

    Returns:
        The ``Path`` of the log file created for this session.
    """
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_file = logs_dir / f"dashapp_{timestamp}.log"

    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    return log_file
