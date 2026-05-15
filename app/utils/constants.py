import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOG_DIR = os.path.join(ROOT_DIR, 'logs')
SETTINGS_DIR = os.path.join(ROOT_DIR, 'settings')

SETTINGS_PATH = os.path.join(SETTINGS_DIR, 'settings.json')
LOG_PATH = os.path.join(LOG_DIR, 'session_log.txt')

BG_COLOR = 'black'
BUTTON_BG = '#1f6feb'
BUTTON_FG = 'white'
FONT_TITLE = ('Arial', 32, 'bold')
FONT_MAIN = ('Arial', 24, 'bold')
WINDOW_TITLE = 'HydroHalo'
WINDOW_SIZE = '800x480'

DEFAULT_SETTINGS = {
    'use_gpio': False,
    'use_sound': True,
    'default_duration': 10,
    'motor_mode': 'placeholder',
    'vesc_port': '/dev/ttyUSB0',
}

RESISTANCE_LEVELS = {
    'Low': 2,
    'Medium': 5,
    'High': 10,
    'Extreme': 15,
}
