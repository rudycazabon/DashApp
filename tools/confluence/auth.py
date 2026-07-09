"""Basic Auth session management for the Confluence tool."""

import json

import requests

from util.paths import CONFLUENCE_CREDENTIALS_PATH

CREDENTIALS_PATH = CONFLUENCE_CREDENTIALS_PATH


def get_auth() -> tuple[requests.Session, str]:
    """Return (session, base_url) configured for Confluence Cloud Basic Auth.

    Reads ``confluence_credentials.json`` from ``~/.dashapp/``. Confluence Cloud
    uses the same Atlassian account (email + API token) as Jira; ``url`` is the
    site root (the Confluence REST API lives under ``<url>/wiki``).
    Format::

        {"url": "https://yourcompany.atlassian.net",
         "email": "you@example.com",
         "api_token": "your-api-token"}

    Raises:
        FileNotFoundError: When ``confluence_credentials.json`` is absent.
        ValueError: When required keys are missing or the URL is malformed.
    """
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"confluence_credentials.json not found at {CREDENTIALS_PATH}. "
            "Create it in ~/.dashapp/ with your Atlassian site URL, email, and "
            "API token."
        )

    creds = json.loads(CREDENTIALS_PATH.read_text())

    missing = [k for k in ("url", "email", "api_token") if k not in creds]
    if missing:
        raise ValueError(
            f"confluence_credentials.json is missing required keys: "
            f"{', '.join(missing)}. "
            'Expected: {"url": "https://yourcompany.atlassian.net", '
            '"email": "you@example.com", "api_token": "your-token"}'
        )

    base_url: str = creds["url"].rstrip("/")
    if not base_url.startswith(("http://", "https://")):
        raise ValueError(
            f"confluence_credentials.json 'url' value looks wrong: {base_url!r}. "
            "It should start with https://, e.g. https://yourcompany.atlassian.net"
        )

    email: str = creds["email"]
    api_token: str = creds["api_token"]

    session = requests.Session()
    session.auth = (email, api_token)
    session.headers.update({"Accept": "application/json"})

    return session, base_url
