"""OAuth 2.0 credential management for the Gmail tool."""

from pathlib import Path
from typing import cast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from util.paths import APP_DIR

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = APP_DIR / "gmail_token.json"

# Resolve credentials.json relative to the project root (three levels up from here:
# tools/gmail/auth.py → tools/gmail/ → tools/ → project root)
CREDENTIALS_PATH = Path(__file__).parent.parent.parent / "credentials.json"


def get_credentials() -> Credentials:
    """Return valid Gmail OAuth credentials, refreshing or re-authorising as needed.

    Raises:
        FileNotFoundError: When credentials.json is absent from the project root.
    """
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"credentials.json not found at {CREDENTIALS_PATH}. "
            "Download it from Google Cloud Console and place it in the project root."
        )

    creds: Credentials | None = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        final_creds = creds
    else:
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        # run_local_server returns a union type; cast to the oauth2 Credentials we expect
        final_creds = cast(Credentials, flow.run_local_server(port=0))

    APP_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(final_creds.to_json())

    return final_creds
