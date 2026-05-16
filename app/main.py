"""Application entrypoint for HydroHalo."""
from __future__ import annotations
import tkinter as tk
from app.controllers.motor_controller import MotorController
from app.controllers.safety_controller import SafetyController
from app.controllers.session_controller import SessionController
from app.gui.app import HydroHaloApp
from app.hardware.vesc_interface import VESCInterface
from app.services.logging_service import configure_logging
from app.services.settings_service import SettingsService

def main() -> None:
    """Bootstrap dependencies and launch Tkinter app."""
    logger = configure_logging()
    settings_service = SettingsService()
    settings = settings_service.load()
    vesc = VESCInterface(port=settings.vesc_port, simulation_mode=settings.simulation_mode, logger=logger)
    safety = SafetyController()
    motor_controller = MotorController(vesc=vesc, safety=safety, logger=logger)
    session_controller = SessionController()

    root = tk.Tk()
    app = HydroHaloApp(root, motor_controller, session_controller, settings_service, settings)
    root.protocol('WM_DELETE_WINDOW', app.on_close)
    root.mainloop()

if __name__ == '__main__':
    main()
