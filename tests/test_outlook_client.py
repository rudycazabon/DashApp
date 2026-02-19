"""Tests for tools/outlook/client.py — Graph API wrapper."""

import re
from unittest.mock import MagicMock, patch

import pytest

from tools.outlook.client import (
    _today_utc_str,
    fetch_messages,
    fetch_todays_messages,
    parse_message,
)

# ---------------------------------------------------------------------------
# fetch_messages
# ---------------------------------------------------------------------------


def test_fetch_messages_returns_value() -> None:
    """fetch_messages returns the 'value' list from the JSON response."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"value": [{"id": "m1"}, {"id": "m2"}]}

    with patch("tools.outlook.client.requests.get", return_value=mock_resp):
        result = fetch_messages("token", "2026-02-19T00:00:00Z")

    assert result == [{"id": "m1"}, {"id": "m2"}]
    mock_resp.raise_for_status.assert_called_once()


def test_fetch_messages_empty_when_no_value_key() -> None:
    """fetch_messages returns [] when 'value' key is absent from response."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {}

    with patch("tools.outlook.client.requests.get", return_value=mock_resp):
        result = fetch_messages("token", "2026-02-19T00:00:00Z")

    assert result == []


def test_fetch_messages_passes_correct_params() -> None:
    """fetch_messages sends the correct params and Authorization header."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"value": []}

    with patch("tools.outlook.client.requests.get", return_value=mock_resp) as mock_get:
        fetch_messages("my-token", "2026-02-19T00:00:00Z")

    _, kwargs = mock_get.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer my-token"
    params = kwargs["params"]
    assert "$filter" in params
    assert "receivedDateTime ge" in params["$filter"]
    assert "$orderby" in params
    assert "$top" in params
    assert "$select" in params


def test_fetch_messages_raises_on_http_error() -> None:
    """fetch_messages propagates HTTPError raised by raise_for_status."""
    import requests as req_lib

    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = req_lib.HTTPError("403")

    with patch("tools.outlook.client.requests.get", return_value=mock_resp):
        with pytest.raises(req_lib.HTTPError):
            fetch_messages("token", "2026-02-19T00:00:00Z")


# ---------------------------------------------------------------------------
# parse_message
# ---------------------------------------------------------------------------


def test_parse_message_normal_fields() -> None:
    """parse_message maps Graph fields to the flat display dict."""
    msg = {
        "from": {"emailAddress": {"address": "alice@example.com"}},
        "subject": "Hello",
        "receivedDateTime": "2026-02-19T09:00:00Z",
        "bodyPreview": "Short preview",
    }
    result = parse_message(msg)
    assert result["from_"] == "alice@example.com"
    assert result["subject"] == "Hello"
    assert result["time"] == "2026-02-19T09:00:00Z"
    assert result["snippet"] == "Short preview"


def test_parse_message_defaults_for_missing_fields() -> None:
    """parse_message uses safe defaults when fields are absent."""
    result = parse_message({})
    assert result["from_"] == "(unknown)"
    assert result["subject"] == "(no subject)"
    assert result["time"] == ""
    assert result["snippet"] == ""


# ---------------------------------------------------------------------------
# _today_utc_str
# ---------------------------------------------------------------------------


def test_today_utc_str_format() -> None:
    """_today_utc_str returns a string matching YYYY-MM-DDT00:00:00Z."""
    value = _today_utc_str()
    assert re.match(r"^\d{4}-\d{2}-\d{2}T00:00:00Z$", value)


# ---------------------------------------------------------------------------
# fetch_todays_messages
# ---------------------------------------------------------------------------


def test_fetch_todays_messages_assembles_results() -> None:
    """fetch_todays_messages calls fetch_messages and parse_message for each item."""
    raw = [{"id": "m1"}, {"id": "m2"}]
    parsed = [
        {"from_": "A", "subject": "S1", "time": "T1", "snippet": "N1"},
        {"from_": "B", "subject": "S2", "time": "T2", "snippet": "N2"},
    ]

    with (
        patch("tools.outlook.client.fetch_messages", return_value=raw) as mock_fetch,
        patch("tools.outlook.client.parse_message", side_effect=parsed) as mock_parse,
        patch(
            "tools.outlook.client._today_utc_str", return_value="2026-02-19T00:00:00Z"
        ),
    ):
        result = fetch_todays_messages("token")

    mock_fetch.assert_called_once_with("token", "2026-02-19T00:00:00Z")
    assert mock_parse.call_count == 2
    assert result == parsed
