"""Single source of truth for application filesystem paths."""

from pathlib import Path

APP_DIR = Path.home() / ".dashapp"
DB_PATH = APP_DIR / "dashapp.db"
LOGS_DIR = APP_DIR / "logs"
