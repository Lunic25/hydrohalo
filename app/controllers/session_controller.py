"""Session orchestration controller."""
from __future__ import annotations
from datetime import datetime
from app.config.constants import LOG_DIR, LOG_PATH
from app.models.session import Session

class SessionController:
    """Starts/stops sessions and records session history."""
    def __init__(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def log_session(self, session: Session) -> None:
        """Append session details to session log."""
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with LOG_PATH.open('a', encoding='utf-8') as handle:
            handle.write(f'{ts} | Level:{session.level} | Duration:{session.duration_seconds}s\n')
