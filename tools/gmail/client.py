"""Thin wrapper around the Gmail REST API."""

from datetime import datetime
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_service(creds: Credentials) -> Any:
    """Build and return an authenticated Gmail API service (gmail v1).

    Returns Any because googleapiclient.Resource uses dynamic attribute
    access that static type-checkers cannot resolve.
    """
    return build("gmail", "v1", credentials=creds)


def fetch_todays_emails(creds: Credentials) -> list[dict[str, str]]:
    """Return messages received today as a list of dicts.

    Fetches metadata headers only: From, Subject, Date.
    Returns up to 50 messages (API default page size).
    Each dict has keys: ``from_``, ``subject``, ``time``, ``snippet``.
    """
    service = get_service(creds)
    today = datetime.now().strftime("%Y/%m/%d")
    query = f"after:{today}"

    result = (
        service.users().messages().list(userId="me", q=query, maxResults=50).execute()
    )

    messages = result.get("messages", [])
    if not messages:
        return []

    emails: list[dict[str, str]] = []
    for msg_stub in messages:
        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg_stub["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )
        headers = {
            h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])
        }
        emails.append(
            {
                "from_": headers.get("From", "(unknown)"),
                "subject": headers.get("Subject", "(no subject)"),
                "time": headers.get("Date", ""),
                "snippet": msg.get("snippet", ""),
            }
        )

    return emails
