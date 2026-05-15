import json
import os
from app.utils.constants import DEFAULT_SETTINGS, SETTINGS_DIR, SETTINGS_PATH


def ensure_settings_dir() -> None:
    os.makedirs(SETTINGS_DIR, exist_ok=True)


def load_settings() -> dict:
    ensure_settings_dir()
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            return data
        except Exception as exc:
            print(f'⚠️ Failed to load settings: {exc}')
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    ensure_settings_dir()
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    except Exception as exc:
        print(f'⚠️ Failed to save settings: {exc}')
