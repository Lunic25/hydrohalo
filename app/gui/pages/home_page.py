"""Home page for resistance selection."""
from __future__ import annotations
import tkinter as tk
from app.config.constants import BG_COLOR, RESISTANCE_LEVELS, ACCENT_CYAN


class HomePage(tk.Frame):
    """Top-level resistance selection page."""

    def __init__(self, parent: tk.Misc, on_level_selected):
        super().__init__(parent, bg=BG_COLOR)
        self.on_level_selected = on_level_selected

        tk.Label(self, text="HydroHalo", bg=BG_COLOR, fg="white", font=("Helvetica", 28, "bold")).grid(row=0, column=0, columnspan=2, pady=(8, 20))

        for i, lvl in enumerate(RESISTANCE_LEVELS):
            tk.Button(
                self,
                text=lvl,
                command=lambda l=lvl: self.on_level_selected(l),
                bg=ACCENT_CYAN,
                font=("Helvetica", 20, "bold"),
                width=10,
                height=3,
            ).grid(row=(i // 2) + 1, column=i % 2, padx=12, pady=12, sticky="nsew")

        for c in range(2):
            self.grid_columnconfigure(c, weight=1)
        for r in range(3):
            self.grid_rowconfigure(r, weight=1)
