"""Tests for tools/gmail/client.py — Gmail API wrapper."""

from unittest.mock import MagicMock, patch

from tools.gmail.client import fetch_todays_emails, get_service


def _make_service(messages: list[dict] | None = None) -> MagicMock:
    """Build a mock Gmail service whose list() call returns *messages*."""
    service = MagicMock()
    list_result = {"messages": messages} if messages is not None else {}
    (
        service.users.return_value.messages.return_value.list.return_value.execute.return_value
    ) = list_result
    return service


def test_fetch_returns_empty_list_when_no_messages() -> None:
    """fetch_todays_emails returns [] when the API returns no messages."""
    mock_creds = MagicMock()
    service = _make_service(messages=None)

    with patch("tools.gmail.client.get_service", return_value=service):
        result = fetch_todays_emails(mock_creds)

    assert result == []


def test_fetch_parses_message_headers() -> None:
    """fetch_todays_emails maps From/Subject/Date headers to dict keys."""
    mock_creds = MagicMock()

    stub = {"id": "msg1"}
    full_msg = {
        "id": "msg1",
        "snippet": "Hello there",
        "payload": {
            "headers": [
                {"name": "From", "value": "Alice <alice@example.com>"},
                {"name": "Subject", "value": "Test subject"},
                {"name": "Date", "value": "Wed, 18 Feb 2026 09:00:00 +0000"},
            ]
        },
    }

    service = _make_service(messages=[stub])
    (
        service.users.return_value.messages.return_value.get.return_value.execute.return_value
    ) = full_msg

    with patch("tools.gmail.client.get_service", return_value=service):
        result = fetch_todays_emails(mock_creds)

    assert len(result) == 1
    email = result[0]
    assert email["from_"] == "Alice <alice@example.com>"
    assert email["subject"] == "Test subject"
    assert email["time"] == "Wed, 18 Feb 2026 09:00:00 +0000"


def test_fetch_includes_snippet() -> None:
    """fetch_todays_emails includes the message snippet in the output dict."""
    mock_creds = MagicMock()

    stub = {"id": "msg2"}
    full_msg = {
        "id": "msg2",
        "snippet": "Snippet text here",
        "payload": {"headers": []},
    }

    service = _make_service(messages=[stub])
    (
        service.users.return_value.messages.return_value.get.return_value.execute.return_value
    ) = full_msg

    with patch("tools.gmail.client.get_service", return_value=service):
        result = fetch_todays_emails(mock_creds)

    assert result[0]["snippet"] == "Snippet text here"


def test_get_service_calls_gmail_v1() -> None:
    """get_service calls build('gmail', 'v1', credentials=...) ."""
    mock_creds = MagicMock()

    with patch("tools.gmail.client.build") as mock_build:
        get_service(mock_creds)

    mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)
