#!/usr/bin/env python3
"""Single application entrypoint for HydroHalo.

Responsibilities:
- Load settings
- Initialize controllers
- Initialize GUI
- Safely handle shutdown
- Catch exceptions cleanly
"""

from __future__ import annotations

import sys
import tkinter as tk
import traceback

from display_gui import HydroHaloGUI, load_settings, ON_PI


def run() -> int:
    app = None
    root = None
    try:
        settings = load_settings()

        if ON_PI and not settings.get("use_gpio", False):
            print("ℹ️ Running on Raspberry Pi with GPIO disabled in settings (safe default).")

        # Initialize GUI + underlying controller(s) owned by GUI.
        root = tk.Tk()
        app = HydroHaloGUI(root, settings)
        root.mainloop()
        return 0

    except KeyboardInterrupt:
        print("Interrupted by user (KeyboardInterrupt).")
        return 130

    except Exception:
        print("Unhandled exception in HydroHalo entrypoint:")
        traceback.print_exc()
        return 1

    finally:
        # Safe shutdown path: always try to stop motor controller and close GUI.
        if app is not None:
            try:
                app.stop_resistance_cycle()
            except Exception:
                pass
            try:
                app.motor.stop()
            except Exception:
                pass

        if root is not None:
            try:
                if root.winfo_exists():
                    root.destroy()
            except Exception:
                pass

        print("Shutdown complete")


if __name__ == "__main__":
    raise SystemExit(run())
