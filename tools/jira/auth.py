"""Basic Auth session management for the Jira tool."""

import json
from pathlib import Path

import requests

# jira_credentials.json lives at the project root (gitignored).
# tools/jira/auth.py → tools/jira/ → tools/ → project root
CREDENTIALS_PATH = Path(__file__).parent.parent.parent / "jira_credentials.json"


def get_auth() -> tuple[requests.Session, str]:
    """Return (session, base_url) configured for Jira REST API Basic Auth.

    Reads ``jira_credentials.json`` from the project root.
    Format::

        {"url": "https://yourcompany.atlassian.net",
         "email": "you@example.com",
         "api_token": "your-api-token"}

    Raises:
        FileNotFoundError: When ``jira_credentials.json`` is absent.
        KeyError: When required keys are missing from the credentials file.
    """
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"jira_credentials.json not found at {CREDENTIALS_PATH}. "
            "Create it at the project root with your Jira URL, email, and API token."
        )

    creds = json.loads(CREDENTIALS_PATH.read_text())

    missing = [k for k in ("url", "email", "api_token") if k not in creds]
    if missing:
        raise ValueError(
            f"jira_credentials.json is missing required keys: {', '.join(missing)}. "
            'Expected: {"url": "https://yourcompany.atlassian.net", '
            '"email": "you@example.com", "api_token": "your-token"}'
        )

    base_url: str = creds["url"].rstrip("/")
    if not base_url.startswith(("http://", "https://")):
        raise ValueError(
            f"jira_credentials.json 'url' value looks wrong: {base_url!r}. "
            "It should start with https://, e.g. https://yourcompany.atlassian.net"
        )

    email: str = creds["email"]
    api_token: str = creds["api_token"]

    session = requests.Session()
    session.auth = (email, api_token)
    session.headers.update({"Accept": "application/json"})

    return session, base_url
