"""Watchdog safety monitoring."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from app.models.safety_status import SafetyLimits, SafetyStatus
from app.models.telemetry import Telemetry


@dataclass(slots=True)
class WatchdogResult:
    tripped: bool
    reason: str = ""


class WatchdogController:
    def __init__(self, safety_status: SafetyStatus | None = None, logger: logging.Logger | None = None) -> None:
        self.status = safety_status or SafetyStatus()
        self.logger = logger or logging.getLogger("hydrohalo.watchdog")
        self.last_telemetry_ts = 0.0
        self.last_encoder_ts = 0.0

    def evaluate(
        self,
        telemetry: Telemetry,
        *,
        serial_connected: bool,
        loop_alive: bool,
        control_loop_age_ms: float,
        control_thread_alive: bool,
    ) -> WatchdogResult:
        now = time.monotonic()
        self.last_telemetry_ts = telemetry.timestamp
        if telemetry.encoder_position is not None:
            self.last_encoder_ts = telemetry.timestamp

        checks = [
            (not serial_connected, "serial_disconnect"),
            (not loop_alive, "stalled_control_loop"),
            (not control_thread_alive, "thread_death"),
            (control_loop_age_ms > SafetyLimits.CONTROL_LOOP_TIMEOUT_MS, "stalled_control_loop"),
            (telemetry.current > SafetyLimits.MAX_CURRENT_A, "excessive_current"),
            (telemetry.rpm > SafetyLimits.MAX_RPM, "motor_runaway"),
            (telemetry.line_length_m > SafetyLimits.MAX_LINE_LENGTH_M, "line_length_exceeded"),
            (telemetry.fault_code != 0, f"controller_fault_{telemetry.fault_code}"),
            (telemetry.current < 0 or telemetry.voltage <= 0, "invalid_sensor_values"),
            ((now - telemetry.timestamp) * 1000.0 > SafetyLimits.TELEMETRY_TIMEOUT_MS, "telemetry_timeout"),
            ((now - self.last_encoder_ts) * 1000.0 > SafetyLimits.ENCODER_TIMEOUT_MS, "encoder_timeout"),
        ]
        for condition, reason in checks:
            if condition:
                self.status.latch_fault(reason)
                self.logger.error("watchdog_trip subsystem=watchdog reason=%s", reason)
                return WatchdogResult(True, reason)
        return WatchdogResult(False)
