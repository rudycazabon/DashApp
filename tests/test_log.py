"""Tests for util/log.py — session logging setup."""

import logging
import re
from pathlib import Path

import pytest

from util.log import setup_logging


@pytest.fixture(autouse=True)
def _clean_root_handlers():
    """Remove any FileHandlers added during a test from the root logger."""
    root = logging.getLogger()
    before = list(root.handlers)
    yield
    for h in list(root.handlers):
        if h not in before:
            h.close()
            root.removeHandler(h)
    # Restore original level
    root.setLevel(logging.WARNING)


def test_setup_logging_creates_logs_dir(tmp_path: Path) -> None:
    """setup_logging creates the logs directory when it does not exist."""
    logs_dir = tmp_path / "nested" / "logs"
    assert not logs_dir.exists()

    setup_logging(logs_dir)

    assert logs_dir.is_dir()


def test_setup_logging_creates_log_file(tmp_path: Path) -> None:
    """setup_logging creates a log file inside the logs directory."""
    log_file = setup_logging(tmp_path)

    assert log_file.exists()
    assert log_file.parent == tmp_path


def test_log_file_name_matches_pattern(tmp_path: Path) -> None:
    """Log file name follows the dashapp_YYYY-MM-DD_HHMMSS.log pattern."""
    log_file = setup_logging(tmp_path)

    assert re.match(r"^dashapp_\d{4}-\d{2}-\d{2}_\d{6}\.log$", log_file.name)


def test_setup_logging_attaches_file_handler(tmp_path: Path) -> None:
    """setup_logging adds a FileHandler to the root logger."""
    root = logging.getLogger()
    handlers_before = len(root.handlers)

    setup_logging(tmp_path)

    file_handlers = [h for h in root.handlers if isinstance(h, logging.FileHandler)]
    assert (
        len(file_handlers)
        == len(
            [
                h
                for h in root.handlers[:handlers_before]
                if isinstance(h, logging.FileHandler)
            ]
        )
        + 1
    )


def test_setup_logging_writes_messages_to_file(tmp_path: Path) -> None:
    """Log messages at INFO and above appear in the log file."""
    log_file = setup_logging(tmp_path)
    logger = logging.getLogger("test.dashapp")

    logger.info("test info message")
    logger.warning("test warning message")
    logger.error("test error message")

    # Flush handlers
    for h in logging.getLogger().handlers:
        h.flush()

    content = log_file.read_text(encoding="utf-8")
    assert "test info message" in content
    assert "test warning message" in content
    assert "test error message" in content


def test_setup_logging_returns_path(tmp_path: Path) -> None:
    """setup_logging returns a Path object pointing to the created log file."""
    result = setup_logging(tmp_path)

    assert isinstance(result, Path)
    assert result.suffix == ".log"
