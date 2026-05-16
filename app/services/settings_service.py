"""Settings persistence service."""
from __future__ import annotations
import json
from dataclasses import asdict
from app.config.constants import SETTINGS_DIR, SETTINGS_PATH
from app.config.settings import AppSettings

class SettingsService:
    """Load and persist application settings."""
    def load(self) -> AppSettings:
        """Load settings from disk with defaults."""
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        if SETTINGS_PATH.exists():
            try:
                data = json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
                return AppSettings(**{**asdict(AppSettings()), **data})
            except Exception:
                return AppSettings()
        return AppSettings()

    def save(self, settings: AppSettings) -> None:
        """Persist settings to disk."""
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(asdict(settings), indent=2), encoding='utf-8')
