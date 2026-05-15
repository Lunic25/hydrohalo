from datetime import datetime
import os
from app.utils.constants import LOG_DIR, LOG_PATH


def ensure_log_dir() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)


def log_session(level: str, duration: int) -> None:
    ensure_log_dir()
    try:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f'{ts} | Level:{level} | Duration:{duration}s\n'
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(entry)
        print('📝', entry.strip())
    except Exception as exc:
        print(f'⚠️ Logging error: {exc}')
