"""Thin wrapper around the Gmail REST API."""

from datetime import datetime
from typing import Any, cast

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_service(creds: Credentials) -> Any:
    """Build and return an authenticated Gmail API service (gmail v1).

    Returns Any because googleapiclient.Resource uses dynamic attribute
    access that static type-checkers cannot resolve.
    """
    return build("gmail", "v1", credentials=creds)


def fetch_message_ids(service: Any, today_str: str) -> list[dict[str, Any]]:
    """Return stub list from Gmail API (id + threadId) for the given date string."""
    result = (
        service.users()
        .messages()
        .list(userId="me", q=f"after:{today_str}", maxResults=50)
        .execute()
    )
    return cast(list[dict[str, Any]], result.get("messages", []))


def fetch_message_detail(service: Any, msg_id: str) -> dict[str, str]:
    """Fetch one message by ID; return dict with from_, subject, time, snippet."""
    msg = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=msg_id,
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"],
        )
        .execute()
    )
    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    return {
        "from_": headers.get("From", "(unknown)"),
        "subject": headers.get("Subject", "(no subject)"),
        "time": headers.get("Date", ""),
        "snippet": msg.get("snippet", ""),
    }


def fetch_todays_emails(creds: Credentials) -> list[dict[str, str]]:
    """Return messages received today as a list of dicts.

    Fetches metadata headers only: From, Subject, Date.
    Returns up to 50 messages (API default page size).
    Each dict has keys: ``from_``, ``subject``, ``time``, ``snippet``.
    """
    service = get_service(creds)
    today = datetime.now().strftime("%Y/%m/%d")
    stubs = fetch_message_ids(service, today)
    return [fetch_message_detail(service, stub["id"]) for stub in stubs]
