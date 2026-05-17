"""Single HydroHalo application entrypoint."""
from __future__ import annotations

import signal
import tkinter as tk

from app.controllers.motor_controller import MotorController
from app.controllers.safety_controller import SafetyController
from app.controllers.session_controller import SessionController
from app.gui.app import HydroHaloApp
from app.gui.splash_screen import SplashScreen
from app.hardware.vesc_interface import VESCInterface
from app.services.logging_service import configure_logging
from app.services.settings_service import SettingsService


def _enforce_safe_startup(settings, logger) -> None:
    """Apply production safety policy before hardware control is enabled."""
    if settings.production_mode and not settings.allow_simulation_in_production:
        settings.simulation_mode = False

    logger.info("Startup safety policy applied: booting IDLE, motor output disabled")


def main() -> None:
    """Bootstrap dependencies and launch kiosk GUI."""
    logger = configure_logging()
    settings_service = SettingsService()
    settings = settings_service.load()
    _enforce_safe_startup(settings, logger)

    vesc = VESCInterface(port=settings.vesc_port, simulation_mode=settings.simulation_mode, logger=logger)
    connected = vesc.connect()
    safety = SafetyController()
    motor_controller = MotorController(vesc=vesc, safety=safety, logger=logger)
    motor_controller.stop()  # force zero output at startup

    if settings.production_mode and not connected:
        logger.error("Hardware unavailable during production startup; staying fail-safe")
        motor_controller.emergency_stop()

    session_controller = SessionController()
    root = tk.Tk()
    app = HydroHaloApp(root, motor_controller, session_controller, settings_service, settings)

    splash = SplashScreen(root, duration_ms=settings.splash_duration_ms)
    root.withdraw()

    def show_main() -> None:
        splash.destroy()
        root.deiconify()

    splash.after(settings.splash_duration_ms, show_main)

    def shutdown(*_args) -> None:
        logger.info("Shutdown requested")
        motor_controller.emergency_stop()
        app.on_close()

    root.protocol("WM_DELETE_WINDOW", shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    root.mainloop()


if __name__ == "__main__":
    main()
