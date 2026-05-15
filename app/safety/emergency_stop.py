from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class EmergencyStopResult:
    should_stop: bool
    reason: Optional[str] = None


class EmergencyStop:
    """Evaluates hard-stop safety conditions from telemetry values."""

    def __init__(self, overspeed_limit_rpm: float = 6000.0):
        self.overspeed_limit_rpm = float(overspeed_limit_rpm)

    def evaluate(self, telemetry: Dict[str, Any]) -> EmergencyStopResult:
        pull_force = telemetry.get('pull_force')
        if pull_force is not None and pull_force <= 0:
            return EmergencyStopResult(True, 'emergency:zero_pull_force')

        encoder_ok = telemetry.get('encoder_ok')
        if encoder_ok is False:
            return EmergencyStopResult(True, 'emergency:encoder_failure')

        rpm = telemetry.get('motor_rpm')
        if rpm is not None and rpm > self.overspeed_limit_rpm:
            return EmergencyStopResult(True, f'emergency:overspeed>{self.overspeed_limit_rpm:.1f}rpm')

        if self._has_invalid_sensor_values(telemetry):
            return EmergencyStopResult(True, 'emergency:invalid_sensor_values')

        return EmergencyStopResult(False)

    @staticmethod
    def _has_invalid_sensor_values(telemetry: Dict[str, Any]) -> bool:
        invalid = telemetry.get('invalid_sensor_values')
        if invalid is True:
            return True

        sensor_values = telemetry.get('sensor_values')
        if isinstance(sensor_values, dict):
            for value in sensor_values.values():
                if value is None:
                    return True
                if isinstance(value, float) and (value != value):
                    return True

        return False
