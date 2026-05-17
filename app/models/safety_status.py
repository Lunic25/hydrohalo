"""Safety model and safety limits for HydroHalo."""
from __future__ import annotations

from dataclasses import dataclass, field


class SafetyLimits:
    MAX_CURRENT_A = 12.0
    MAX_RPM = 5500.0
    MAX_LINE_LENGTH_M = 35.0
    MIN_TENSION_THRESHOLD = 0.25
    MAX_ACCELERATION = 1500.0
    CONTROL_LOOP_TIMEOUT_MS = 100.0
    TELEMETRY_TIMEOUT_MS = 300.0
    ENCODER_TIMEOUT_MS = 300.0


@dataclass(slots=True)
class SafetyStatus:
    fault_latched: bool = False
    emergency_active: bool = False
    reason: str = ""
    watchdog_events: list[str] = field(default_factory=list)

    def latch_fault(self, reason: str) -> None:
        self.fault_latched = True
        self.emergency_active = True
        self.reason = reason
        self.watchdog_events.append(reason)

    def clear(self) -> None:
        self.fault_latched = False
        self.emergency_active = False
        self.reason = ""
