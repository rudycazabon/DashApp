"""Tests for tools/confluence/client.py — Confluence Cloud REST API wrapper."""

from unittest.mock import MagicMock

import pytest

from tools.confluence.client import (
    fetch_pages,
    fetch_spaces,
    parse_page,
    parse_space,
)

BASE_URL = "https://example.atlassian.net"


def _mock_session(json_data: dict) -> MagicMock:
    """Return a mock session whose get() call returns json_data."""
    session = MagicMock()
    session.get.return_value.json.return_value = json_data
    return session


# ---------------------------------------------------------------------------
# fetch_spaces
# ---------------------------------------------------------------------------


def test_fetch_spaces_returns_results() -> None:
    """fetch_spaces returns the 'results' list from the response."""
    session = _mock_session({"results": [{"id": "1", "key": "ENG", "name": "Eng"}]})

    result = fetch_spaces(session, BASE_URL)

    assert result == [{"id": "1", "key": "ENG", "name": "Eng"}]
    session.get.return_value.raise_for_status.assert_called_once()


def test_fetch_spaces_empty_when_no_results_key() -> None:
    """fetch_spaces returns [] when 'results' key is absent."""
    session = _mock_session({})

    result = fetch_spaces(session, BASE_URL)

    assert result == []


def test_fetch_spaces_raises_on_http_error() -> None:
    """fetch_spaces propagates HTTPError from raise_for_status."""
    import requests as req_lib

    session = MagicMock()
    session.get.return_value.raise_for_status.side_effect = req_lib.HTTPError("403")

    with pytest.raises(req_lib.HTTPError):
        fetch_spaces(session, BASE_URL)


# ---------------------------------------------------------------------------
# parse_space
# ---------------------------------------------------------------------------


def test_parse_space_normal_fields() -> None:
    """parse_space maps space fields to the flat display dict."""
    space = {"id": 12345, "key": "ENG", "name": "Engineering", "type": "global"}

    result = parse_space(space)

    assert result["id"] == "12345"
    assert result["key"] == "ENG"
    assert result["name"] == "Engineering"
    assert result["type"] == "global"


def test_parse_space_defaults_for_missing_fields() -> None:
    """parse_space uses safe defaults when fields are absent."""
    result = parse_space({})

    assert result["id"] == ""
    assert result["key"] == ""
    assert result["name"] == "(unnamed)"
    assert result["type"] == ""


# ---------------------------------------------------------------------------
# fetch_pages
# ---------------------------------------------------------------------------


def test_fetch_pages_returns_results() -> None:
    """fetch_pages returns the 'results' list from the response."""
    session = _mock_session({"results": [{"id": "10"}, {"id": "11"}]})

    result = fetch_pages(session, BASE_URL)

    assert result == [{"id": "10"}, {"id": "11"}]


def test_fetch_pages_empty_when_no_results_key() -> None:
    """fetch_pages returns [] when 'results' key is absent."""
    session = _mock_session({})

    result = fetch_pages(session, BASE_URL)

    assert result == []


def test_fetch_pages_raises_on_http_error() -> None:
    """fetch_pages propagates HTTPError from raise_for_status."""
    import requests as req_lib

    session = MagicMock()
    session.get.return_value.raise_for_status.side_effect = req_lib.HTTPError("401")

    with pytest.raises(req_lib.HTTPError):
        fetch_pages(session, BASE_URL)


# ---------------------------------------------------------------------------
# parse_page
# ---------------------------------------------------------------------------


def test_parse_page_normal_fields() -> None:
    """parse_page maps page fields, using the version timestamp for 'updated'."""
    page = {
        "id": 987,
        "title": "Runbook",
        "status": "current",
        "spaceId": 12345,
        "createdAt": "2026-01-01T00:00:00.000Z",
        "version": {"number": 7, "createdAt": "2026-07-01T09:30:00.000Z"},
    }

    result = parse_page(page)

    assert result["id"] == "987"
    assert result["title"] == "Runbook"
    assert result["status"] == "current"
    assert result["space_id"] == "12345"
    assert result["version"] == "7"
    assert result["updated"] == "2026-07-01T09:30:00.000Z"


def test_parse_page_falls_back_to_created_at() -> None:
    """parse_page uses the page createdAt when no version timestamp is present."""
    page = {
        "id": "5",
        "title": "Draft",
        "status": "draft",
        "spaceId": "1",
        "createdAt": "2026-02-02T12:00:00.000Z",
    }

    result = parse_page(page)

    assert result["version"] == ""
    assert result["updated"] == "2026-02-02T12:00:00.000Z"


def test_parse_page_defaults_for_missing_fields() -> None:
    """parse_page uses safe defaults when all fields are absent."""
    result = parse_page({})

    assert result["id"] == ""
    assert result["title"] == "(untitled)"
    assert result["status"] == ""
    assert result["space_id"] == ""
    assert result["version"] == ""
    assert result["updated"] == ""
