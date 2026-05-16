"""Home page for resistance selection."""
from __future__ import annotations
import tkinter as tk
from app.config.constants import BG_COLOR, RESISTANCE_LEVELS, ACCENT_CYAN

class HomePage(tk.Frame):
    """Top-level resistance selection page."""
    def __init__(self, parent: tk.Misc, on_level_selected):
        super().__init__(parent, bg=BG_COLOR)
        self.on_level_selected = on_level_selected
        for i, lvl in enumerate(RESISTANCE_LEVELS):
            tk.Button(self, text=lvl, command=lambda l=lvl: self.on_level_selected(l), bg=ACCENT_CYAN).grid(row=i // 2, column=i % 2, padx=6, pady=6)
