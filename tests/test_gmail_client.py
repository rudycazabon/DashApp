"""Tests for tools/gmail/client.py — Gmail API wrapper."""

from unittest.mock import MagicMock, patch

from tools.gmail.client import (
    fetch_message_detail,
    fetch_message_ids,
    fetch_todays_emails,
    get_service,
)


def _make_service(messages: list[dict] | None = None) -> MagicMock:
    """Build a mock Gmail service whose list() call returns *messages*."""
    service = MagicMock()
    list_result = {"messages": messages} if messages is not None else {}
    (
        service.users.return_value.messages.return_value.list.return_value.execute.return_value
    ) = list_result
    return service


# ---------------------------------------------------------------------------
# fetch_todays_emails (existing tests — backward compat)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# fetch_message_ids
# ---------------------------------------------------------------------------


def test_fetch_message_ids_returns_stubs() -> None:
    """fetch_message_ids returns the list of stubs from the API."""
    service = _make_service(messages=[{"id": "a"}, {"id": "b"}])

    result = fetch_message_ids(service, "2026/02/19")

    assert result == [{"id": "a"}, {"id": "b"}]


def test_fetch_message_ids_empty_when_no_messages_key() -> None:
    """fetch_message_ids returns [] when API response has no 'messages' key."""
    service = MagicMock()
    execute = service.users.return_value.messages.return_value.list.return_value.execute
    execute.return_value = {}

    result = fetch_message_ids(service, "2026/02/19")

    assert result == []


def test_fetch_message_ids_passes_correct_query() -> None:
    """fetch_message_ids passes the date string in the 'q' parameter."""
    service = _make_service(messages=[])

    fetch_message_ids(service, "2026/02/19")

    service.users.return_value.messages.return_value.list.assert_called_once_with(
        userId="me", q="after:2026/02/19", maxResults=50
    )


# ---------------------------------------------------------------------------
# fetch_message_detail
# ---------------------------------------------------------------------------


def test_fetch_message_detail_parses_headers() -> None:
    """fetch_message_detail maps From/Subject/Date headers to dict keys."""
    service = MagicMock()
    execute = service.users.return_value.messages.return_value.get.return_value.execute
    execute.return_value = {
        "id": "msg1",
        "snippet": "Hello",
        "payload": {
            "headers": [
                {"name": "From", "value": "Bob <bob@example.com>"},
                {"name": "Subject", "value": "Hi there"},
                {"name": "Date", "value": "Thu, 19 Feb 2026 10:00:00 +0000"},
            ]
        },
    }

    result = fetch_message_detail(service, "msg1")

    assert result["from_"] == "Bob <bob@example.com>"
    assert result["subject"] == "Hi there"
    assert result["time"] == "Thu, 19 Feb 2026 10:00:00 +0000"
    assert result["snippet"] == "Hello"


def test_fetch_message_detail_defaults_for_missing_fields() -> None:
    """fetch_message_detail uses safe defaults when headers/snippet absent."""
    service = MagicMock()
    execute = service.users.return_value.messages.return_value.get.return_value.execute
    execute.return_value = {
        "id": "msg2",
        "payload": {"headers": []},
    }

    result = fetch_message_detail(service, "msg2")

    assert result["from_"] == "(unknown)"
    assert result["subject"] == "(no subject)"
    assert result["time"] == ""
    assert result["snippet"] == ""


def test_fetch_todays_emails_assembles_results() -> None:
    """fetch_todays_emails calls fetch_message_ids then fetch_message_detail."""
    mock_creds = MagicMock()

    with (
        patch("tools.gmail.client.get_service") as mock_get_service,
        patch(
            "tools.gmail.client.fetch_message_ids",
            return_value=[{"id": "x1"}, {"id": "x2"}],
        ) as mock_ids,
        patch(
            "tools.gmail.client.fetch_message_detail",
            side_effect=[
                {"from_": "A", "subject": "S1", "time": "T1", "snippet": "N1"},
                {"from_": "B", "subject": "S2", "time": "T2", "snippet": "N2"},
            ],
        ) as mock_detail,
    ):
        result = fetch_todays_emails(mock_creds)

    mock_get_service.assert_called_once_with(mock_creds)
    assert mock_ids.call_count == 1
    assert mock_detail.call_count == 2
    assert len(result) == 2
    assert result[0]["subject"] == "S1"
    assert result[1]["subject"] == "S2"
