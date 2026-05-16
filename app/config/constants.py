"""Application-wide constants for HydroHalo."""
from __future__ import annotations
from pathlib import Path
APP_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = APP_DIR.parent
LOG_DIR = REPO_ROOT / 'logs'
SETTINGS_DIR = REPO_ROOT / 'settings'
LOG_PATH = LOG_DIR / 'session_log.txt'
SETTINGS_PATH = SETTINGS_DIR / 'settings.json'
BG_COLOR = 'black'
ACCENT_CYAN = '#45FFFF'
ACCENT_WARN = '#FF6B6B'
FONT_TITLE = ('Helvetica', 28, 'bold')
FONT_TEXT = ('Helvetica', 16)
DURATION_OPTIONS = [5, 10, 12, 15]
RESISTANCE_LEVELS = ['Low', 'Medium', 'High', 'Custom']
LEVEL_TO_CURRENT = {'Low': 2.0, 'Medium': 5.0, 'High': 8.0, 'Custom': 3.0}
WATCHDOG_TIMEOUT_SECONDS = 1.5
OVERSPEED_LIMIT_RPM = 6000.0
