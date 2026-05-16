"""Motor controller abstraction with fail-safe shutdown."""
from __future__ import annotations
import threading
import time
from app.config.constants import LEVEL_TO_CURRENT
from app.controllers.safety_controller import SafetyController
from app.hardware.vesc_interface import VESCInterface

class MotorController:
    """High-level motor control independent from GUI and pyvesc."""
    def __init__(self, vesc: VESCInterface, safety: SafetyController, logger=None):
        self.vesc = vesc
        self.safety = safety
        self.logger = logger
        self._lock = threading.Lock()
        self._running = False
        self._level = 'Low'
        self._thread: threading.Thread | None = None
        self.vesc.connect()

    def start(self, level: str) -> None:
        """Start continuous control loop for selected resistance level."""
        with self._lock:
            self._level = level
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        """Stop control loop and bring motor to safe state."""
        with self._lock:
            self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        self.vesc.stop()

    def emergency_stop(self) -> None:
        """Force immediate fail-safe shutdown."""
        with self._lock:
            self._running = False
        self.vesc.emergency_shutdown()

    def _run_loop(self) -> None:
        while True:
            with self._lock:
                if not self._running:
                    break
                level = self._level
            telemetry = self.vesc.read_telemetry()
            decision = self.safety.evaluate(telemetry)
            if decision.should_stop_motor:
                self.emergency_stop()
                break
            self.vesc.set_current(float(LEVEL_TO_CURRENT.get(level, LEVEL_TO_CURRENT['Low'])))
            time.sleep(0.25)
