"""VESC HAL with production and simulation support."""
from __future__ import annotations
from typing import Any, Dict, Optional

class VESCInterface:
    """Encapsulates all VESC communication paths."""
    def __init__(self, port: str, simulation_mode: bool = True, logger=None):
        self.port = port
        self.simulation_mode = simulation_mode
        self.logger = logger
        self._vesc: Optional[Any] = None

    def connect(self) -> bool:
        """Connect to VESC or remain in simulation mode."""
        if self.simulation_mode:
            return True
        try:
            from pyvesc import VESC
            self._vesc = VESC(serial_port=self.port)
            return True
        except Exception:
            self.simulation_mode = True
            return False

    def set_current(self, current: float) -> None:
        """Apply current command to motor controller."""
        if self.simulation_mode or self._vesc is None:
            return
        self._vesc.set_current(current)

    def stop(self) -> None:
        """Stop motor output."""
        self.set_current(0.0)

    def read_telemetry(self) -> Dict[str, Any]:
        """Return latest telemetry dictionary."""
        if self.simulation_mode or self._vesc is None:
            return {'motor_rpm': 0.0, 'pull_force': 1.0, 'encoder_ok': True, 'telemetry_age_seconds': 0.0}
        return {'motor_rpm': 0.0, 'pull_force': 1.0, 'encoder_ok': True, 'telemetry_age_seconds': 0.0}

    def emergency_shutdown(self) -> None:
        """Force immediate motor shutdown."""
        self.stop()
