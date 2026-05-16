"""Tkinter GUI app composition root."""
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from app.config.constants import BG_COLOR, DURATION_OPTIONS
from app.models.session import Session
from app.gui.pages.home_page import HomePage

class HydroHaloApp:
    """GUI facade that depends only on controllers/services."""
    def __init__(self, root: tk.Tk, motor_controller, session_controller, settings_service, settings):
        self.root = root
        self.motor_controller = motor_controller
        self.session_controller = session_controller
        self.settings_service = settings_service
        self.settings = settings
        self._job = None
        self._remaining = 0
        self.root.configure(bg=BG_COLOR)
        self.root.title('HydroHalo')
        HomePage(root, self.open_duration_dialog).pack(pady=12)

    def open_duration_dialog(self, level: str) -> None:
        dlg = tk.Toplevel(self.root)
        var = tk.IntVar(value=self.settings.default_duration)
        tk.OptionMenu(dlg, var, *DURATION_OPTIONS).pack(pady=6)
        status = tk.Label(dlg, text='')
        status.pack()
        tk.Button(dlg, text='Start', command=lambda: self.start_cycle(level, int(var.get()), status)).pack()

    def start_cycle(self, level: str, seconds: int, label: tk.Label) -> None:
        self.stop_cycle()
        self.motor_controller.start(level)
        self.session_controller.log_session(Session(level=level, duration_seconds=seconds))
        self._remaining = seconds
        def tick():
            if self._remaining <= 0:
                self.motor_controller.stop()
                label.config(text='Complete')
                return
            self._remaining -= 1
            label.config(text=f'Remaining: {self._remaining}s')
            self._job = self.root.after(1000, tick)
        tick()

    def stop_cycle(self) -> None:
        if self._job:
            self.root.after_cancel(self._job)
            self._job = None
        self.motor_controller.stop()

    def on_close(self) -> None:
        self.stop_cycle()
        self.settings_service.save(self.settings)
        messagebox.showinfo('HydroHalo', 'Shutting down safely.')
        self.root.destroy()
