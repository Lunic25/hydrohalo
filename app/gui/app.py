"""Tkinter GUI app composition root."""
from __future__ import annotations
import tkinter as tk

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
        self.root.title("HydroHalo")
        self._configure_kiosk_mode()
        HomePage(root, self.open_duration_dialog).pack(fill="both", expand=True, padx=10, pady=10)

    def _configure_kiosk_mode(self) -> None:
        if self.settings.production_mode:
            self.root.attributes("-fullscreen", True)
            if self.settings.hide_cursor:
                self.root.config(cursor="none")
            self.root.bind("<Escape>", lambda _event: "break")

    def open_duration_dialog(self, level: str) -> None:
        dlg = tk.Toplevel(self.root)
        dlg.configure(bg=BG_COLOR)
        dlg.attributes("-topmost", True)

        var = tk.IntVar(value=self.settings.default_duration)
        tk.Label(dlg, text="Duration (sec)", bg=BG_COLOR, fg="white", font=("Helvetica", 18, "bold")).pack(pady=10)
        tk.OptionMenu(dlg, var, *DURATION_OPTIONS).pack(pady=8)
        status = tk.Label(dlg, text="", bg=BG_COLOR, fg="white", font=("Helvetica", 16))
        status.pack(pady=8)
        tk.Button(dlg, text="Start", font=("Helvetica", 18, "bold"), width=12, height=2, command=lambda: self.start_cycle(level, int(var.get()), status)).pack(pady=10)

    def start_cycle(self, level: str, seconds: int, label: tk.Label) -> None:
        self.stop_cycle()
        self.motor_controller.start(level)
        self.session_controller.log_session(Session(level=level, duration_seconds=seconds))
        self._remaining = seconds

        def tick():
            if self._remaining <= 0:
                self.motor_controller.stop()
                label.config(text="Complete")
                return
            self._remaining -= 1
            label.config(text=f"Remaining: {self._remaining}s")
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
        self.root.destroy()
