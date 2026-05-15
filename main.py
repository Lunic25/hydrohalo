#!/usr/bin/env python3
"""HydroHalo main entry point."""

import tkinter as tk
from app.gui.main_window import HydroHaloGUI
from app.utils.settings import load_settings, save_settings


def main():
    settings = load_settings()
    root = tk.Tk()
    app = HydroHaloGUI(root, settings)
    root.protocol('WM_DELETE_WINDOW', app.on_close)
    try:
        root.mainloop()
    finally:
        save_settings(settings)


if __name__ == '__main__':
    main()
