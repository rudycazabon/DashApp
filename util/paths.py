"""Single source of truth for application filesystem paths."""

from pathlib import Path

APP_DIR = Path.home() / ".dashapp"
DB_PATH = APP_DIR / "dashapp.db"
LOGS_DIR = APP_DIR / "logs"

# Credential files — all stored in APP_DIR, never in the project root
JIRA_CREDENTIALS_PATH = APP_DIR / "jira_credentials.json"
CONFLUENCE_CREDENTIALS_PATH = APP_DIR / "confluence_credentials.json"
