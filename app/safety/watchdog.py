from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WatchdogResult:
    tripped: bool
    reason: Optional[str] = None


class Watchdog:
    """Monitors telemetry freshness and detects communications timeouts."""

    def __init__(self, timeout_seconds: float = 1.5):
        self.timeout_seconds = float(timeout_seconds)

    def evaluate(self, last_telemetry_age_seconds: Optional[float]) -> WatchdogResult:
        if last_telemetry_age_seconds is None:
            return WatchdogResult(tripped=True, reason='watchdog:telemetry_missing')

        if last_telemetry_age_seconds > self.timeout_seconds:
            return WatchdogResult(
                tripped=True,
                reason=f'watchdog:timeout>{self.timeout_seconds:.2f}s',
            )

        return WatchdogResult(tripped=False)
