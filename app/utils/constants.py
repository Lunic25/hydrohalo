import os
import platform
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOG_DIR = os.path.join(ROOT_DIR, 'logs')
SETTINGS_DIR = os.path.join(ROOT_DIR, 'settings')
ASSETS_DIR = os.path.join(ROOT_DIR, 'app', 'assets')

SETTINGS_PATH = os.path.join(SETTINGS_DIR, 'settings.json')
LOG_PATH = os.path.join(LOG_DIR, 'session_log.txt')

BG_COLOR = 'black'
ACCENT_CYAN = '#45FFFF'
ACCENT_WARN = '#FF6B6B'
FONT_TITLE = ('Helvetica', 28, 'bold')
FONT_TEXT = ('Helvetica', 16)

DEFAULT_SETTINGS = {
    'use_gpio': False,
    'use_sound': True,
    'default_duration': 10,
    'motor_mode': 'placeholder',
    'vesc_port': '/dev/ttyUSB0',
}

DURATION_OPTIONS = [5, 10, 12, 15]
RESISTANCE_LEVELS = ['Low', 'Medium', 'High', 'Custom']


def is_raspberry_pi() -> bool:
    try:
        if sys.platform.startswith('linux'):
            try:
                with open('/proc/device-tree/model', 'r', encoding='utf-8') as f:
                    if 'raspberry' in f.read().lower():
                        return True
            except Exception:
                pass
        return 'raspberrypi' in platform.uname().node.lower()
    except Exception:
        return False


ON_PI = is_raspberry_pi()
