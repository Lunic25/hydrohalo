"""Lightweight splash screen for HydroHalo startup."""
from __future__ import annotations

from pathlib import Path
import tkinter as tk


class SplashScreen(tk.Toplevel):
    """Fullscreen black splash showing centered HydroHalo logo/text."""

    def __init__(self, parent: tk.Tk, duration_ms: int = 2500) -> None:
        super().__init__(parent)
        self.duration_ms = duration_ms
        self.configure(bg="black")
        self.overrideredirect(True)

        try:
            self.attributes("-fullscreen", True)
        except tk.TclError:
            self.state("zoomed")

        frame = tk.Frame(self, bg="black")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        logo = self._load_logo_image()
        if logo is not None:
            label = tk.Label(frame, image=logo, bg="black", borderwidth=0, highlightthickness=0)
            label.image = logo
            label.pack()
        else:
            tk.Label(
                frame,
                text="HydroHalo",
                fg="#45FFFF",
                bg="black",
                font=("Helvetica", 42, "bold"),
            ).pack()

    def _load_logo_image(self) -> tk.PhotoImage | None:
        """Load logo with robust fallbacks and downscaling for small screens."""
        candidates = [
            Path(__file__).resolve().parents[2] / "assets" / "hydrohalo_logo.png",
            Path(__file__).resolve().parents[2] / "assets" / "logo.png",
            Path(__file__).resolve().parents[2] / "app" / "assets" / "hydrohalo_logo.png",
        ]

        for path in candidates:
            if not path.exists():
                continue
            try:
                image = tk.PhotoImage(file=str(path))
                width = max(image.width(), 1)
                max_width = 480
                scale = max(1, width // max_width)
                if scale > 1:
                    image = image.subsample(scale, scale)
                return image
            except tk.TclError:
                continue
        return None
