"""Standalone Gmail connection diagnostic — run with: uv run python diagnose_gmail.py"""

from tools.gmail.auth import CREDENTIALS_PATH, TOKEN_PATH, get_credentials
from tools.gmail.client import fetch_todays_emails


def main() -> None:
    print(f"credentials.json path : {CREDENTIALS_PATH}")
    print(f"  exists              : {CREDENTIALS_PATH.exists()}")
    print(f"token path            : {TOKEN_PATH}")
    print(f"  exists              : {TOKEN_PATH.exists()}")
    print()

    print("Obtaining credentials…")
    try:
        creds = get_credentials()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    print(f"Credentials valid     : {creds.valid}")
    print(f"Credentials expired   : {creds.expired}")
    print()

    print("Fetching today's emails…")
    try:
        emails = fetch_todays_emails(creds)
    except Exception as e:
        print(f"ERROR fetching emails: {e}")
        return

    print(f"Messages found        : {len(emails)}")
    for i, email in enumerate(emails[:5], 1):
        print(f"\n  [{i}] From   : {email['from_']}")
        print(f"       Subject: {email['subject']}")
        print(f"       Time   : {email['time']}")
        print(f"       Snippet: {email['snippet'][:80]}")

    if len(emails) > 5:
        print(f"\n  … and {len(emails) - 5} more.")


if __name__ == "__main__":
    main()
