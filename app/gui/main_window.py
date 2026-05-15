import tkinter as tk
from app.control.motor_controller import MotorController
from app.utils.constants import BG_COLOR, BUTTON_BG, BUTTON_FG, FONT_MAIN, FONT_TITLE, RESISTANCE_LEVELS, WINDOW_SIZE, WINDOW_TITLE
from app.utils.logger import log_session
from app.utils.settings import save_settings


class HydroHaloGUI:
    def __init__(self, root: tk.Tk, settings: dict):
        self.root = root
        self.settings = settings
        self.motor = MotorController(settings)

        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BG_COLOR)
        self.root.attributes('-fullscreen', True)

        tk.Label(root, text='Select Resistance Level', fg='white', bg=BG_COLOR, font=FONT_TITLE).pack(pady=20)

        for name, current in RESISTANCE_LEVELS.items():
            tk.Button(
                root,
                text=name,
                font=FONT_MAIN,
                width=12,
                height=2,
                bg=BUTTON_BG,
                fg=BUTTON_FG,
                command=lambda level=current, label=name: self.start_resistance(level, label),
            ).pack(pady=12)

        tk.Button(root, text='STOP', font=FONT_MAIN, width=12, height=2, bg='#aa3333', fg='white', command=self.stop_resistance).pack(pady=20)
        tk.Button(root, text='Exit', font=('Arial', 18), bg='gray', fg='white', command=self.on_close).pack(side='bottom', pady=20)

    def start_resistance(self, current: float, label: str):
        self.motor.start(current)
        log_session(label, self.settings.get('default_duration', 10))

    def stop_resistance(self):
        self.motor.stop()

    def on_close(self):
        self.motor.stop()
        save_settings(self.settings)
        self.root.destroy()
