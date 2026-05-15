import os
import sys
import time
import tkinter as tk
from tkinter import messagebox

from app.control.motor_controller import MotorController
from app.utils.constants import (
    ACCENT_CYAN,
    ACCENT_WARN,
    BG_COLOR,
    DURATION_OPTIONS,
    FONT_TEXT,
    FONT_TITLE,
    LOG_PATH,
    ON_PI,
    RESISTANCE_LEVELS,
)
from app.utils.logger import log_session
from app.utils.settings import save_settings

try:
    from PIL import Image, ImageTk
except Exception:
    Image = ImageTk = None


class HydroHaloGUI:
    def __init__(self, root: tk.Tk, settings: dict):
        self.root = root
        self.settings = settings
        self.motor = MotorController(settings)
        self._countdown_job = None
        self._countdown_remaining = 0

        self._setup_root()
        self._build_widgets()

    def _setup_root(self):
        self.root.title('HydroHalo')
        self.root.configure(bg=BG_COLOR)
        self.root.geometry('800x480')
        self.root.minsize(600, 360)
        try:
            if ON_PI:
                self.root.tk.call('tk', 'scaling', 1.0)
        except Exception:
            pass

    def _build_widgets(self):
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'hydrohalo_logo.png')
        if Image and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path).resize((140, 140))
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(self.root, image=photo, bg=BG_COLOR)
                lbl.image = photo
                lbl.pack(pady=6)
            except Exception:
                tk.Label(self.root, text='HYDROHALO', fg=ACCENT_CYAN, bg=BG_COLOR, font=FONT_TITLE).pack(pady=8)
        else:
            tk.Label(self.root, text='HYDROHALO', fg=ACCENT_CYAN, bg=BG_COLOR, font=FONT_TITLE).pack(pady=8)

        tk.Label(self.root, text='Select Resistance Level:', fg='white', bg=BG_COLOR, font=FONT_TEXT).pack(pady=8)
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(pady=6)

        for i, lvl in enumerate(RESISTANCE_LEVELS):
            tk.Button(
                frame,
                text=lvl,
                width=12,
                height=2,
                command=lambda l=lvl: self.open_duration_dialog(l),
                bg=ACCENT_CYAN,
                fg='black',
                font=('Helvetica', 12, 'bold'),
            ).grid(row=i // 2, column=i % 2, padx=8, pady=8)

        status = 'Raspberry Pi' if ON_PI else 'PC/Mac'
        self.status_var = tk.StringVar(value=f"{status} | GPIO: {'Enabled' if self.settings.get('use_gpio') else 'Disabled'}")
        tk.Label(self.root, textvariable=self.status_var, fg='gray', bg=BG_COLOR, font=('Helvetica', 10), anchor='w').pack(side='bottom', fill='x', padx=6, pady=4)

        extra = tk.Frame(self.root, bg=BG_COLOR)
        extra.pack(pady=8)
        tk.Button(extra, text='View Session History', command=self.open_history, width=18, bg='#AAAAFF', fg='black').grid(row=0, column=0, padx=5)
        tk.Button(extra, text='Settings', command=self.open_settings, width=12, bg='#FFD700', fg='black').grid(row=0, column=1, padx=5)

    def open_duration_dialog(self, level):
        dlg = tk.Toplevel(self.root)
        dlg.title(f'{level} duration')
        dlg.configure(bg=BG_COLOR)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=f'Set duration for {level}:', fg='white', bg=BG_COLOR, font=('Helvetica', 12)).pack(pady=8)
        var = tk.IntVar(value=self.settings.get('default_duration', 10))
        tk.OptionMenu(dlg, var, *DURATION_OPTIONS).pack(pady=6)

        countdown_label = tk.Label(dlg, text='', fg='#00BFFF', bg=BG_COLOR, font=('Helvetica', 12))
        countdown_label.pack(pady=8)

        def on_start():
            duration = int(var.get())
            self.start_resistance_cycle(level, duration, countdown_label, confirm_btn)
            confirm_btn.config(state='disabled')

        confirm_btn = tk.Button(dlg, text='Start', command=on_start, bg=ACCENT_CYAN, fg='black')
        confirm_btn.pack(pady=6)
        tk.Button(dlg, text='Cancel', command=dlg.destroy, bg=ACCENT_WARN, fg='white').pack(pady=4)

    def start_resistance_cycle(self, level, duration_seconds, status_label, control_button):
        self.stop_resistance_cycle()
        self.motor.start(level)
        log_session(level, duration_seconds)
        self._countdown_remaining = duration_seconds
        status_label.config(text=f'Time remaining: {self._format_time(self._countdown_remaining)}')

        def tick():
            if self._countdown_remaining <= 0:
                status_label.config(text='✅ Resistance cycle complete!')
                self.motor.stop()
                self._play_sound()
                if control_button.winfo_exists():
                    control_button.config(state='normal')
                return
            self._countdown_remaining -= 1
            status_label.config(text=f'Time remaining: {self._format_time(self._countdown_remaining)}')
            self._countdown_job = self.root.after(1000, tick)

        self._countdown_job = self.root.after(1000, tick)

    def stop_resistance_cycle(self):
        if self._countdown_job:
            try:
                self.root.after_cancel(self._countdown_job)
            except Exception:
                pass
            self._countdown_job = None
        self.motor.stop()

    def open_history(self):
        dlg = tk.Toplevel(self.root)
        dlg.title('Session History')
        dlg.configure(bg=BG_COLOR)
        dlg.geometry('600x400')
        text = tk.Text(dlg, bg=BG_COLOR, fg='white', wrap='word')
        text.pack(expand=True, fill='both', padx=10, pady=10)
        if os.path.exists(LOG_PATH):
            text.insert('1.0', open(LOG_PATH, 'r', encoding='utf-8').read() or 'No sessions recorded yet.')
        else:
            text.insert('1.0', 'No sessions recorded yet.')
        text.config(state='disabled')

    def open_settings(self):
        dlg = tk.Toplevel(self.root)
        dlg.title('Settings')
        dlg.configure(bg=BG_COLOR)
        dlg.transient(self.root)
        dlg.grab_set()
        gpio_var = tk.BooleanVar(value=self.settings.get('use_gpio', False))
        sound_var = tk.BooleanVar(value=self.settings.get('use_sound', True))
        motor_mode_var = tk.StringVar(value=self.settings.get('motor_mode', 'placeholder'))
        tk.Checkbutton(dlg, text='Enable GPIO (Raspberry Pi)', variable=gpio_var, bg=BG_COLOR, fg='white').pack(pady=4)
        tk.Checkbutton(dlg, text='Enable Sound Alerts', variable=sound_var, bg=BG_COLOR, fg='white').pack(pady=4)
        tk.OptionMenu(dlg, motor_mode_var, 'placeholder', 'vesc_serial').pack(pady=2)

        def save():
            self.settings['use_gpio'] = bool(gpio_var.get())
            self.settings['use_sound'] = bool(sound_var.get())
            self.settings['motor_mode'] = motor_mode_var.get()
            save_settings(self.settings)
            self.motor.mode = self.settings.get('motor_mode', 'placeholder')
            messagebox.showinfo('Settings', 'Settings saved')
            dlg.destroy()

        tk.Button(dlg, text='Save', command=save, bg=ACCENT_CYAN, fg='black').pack(pady=6)

    def _play_sound(self):
        if not self.settings.get('use_sound', True):
            return
        if ON_PI:
            os.system('aplay /usr/share/sounds/alsa/Front_Center.wav >/dev/null 2>&1 &')
        elif sys.platform.startswith('win'):
            import winsound
            winsound.Beep(1000, 400)
        else:
            print('\a', end='', flush=True)

    @staticmethod
    def _format_time(seconds):
        m, s = divmod(max(0, int(seconds)), 60)
        return f'{m:02d}:{s:02d}'

    def on_close(self):
        self.stop_resistance_cycle()
        time.sleep(0.05)
        save_settings(self.settings)
        self.root.destroy()
