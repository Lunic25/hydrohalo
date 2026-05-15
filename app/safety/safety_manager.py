from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.safety.emergency_stop import EmergencyStop
from app.safety.shutdown_sequence import ShutdownEvent, ShutdownSequence
from app.safety.watchdog import Watchdog


@dataclass(frozen=True)
class SafetyDecision:
    healthy: bool
    should_stop_motor: bool
    reason: Optional[str] = None
    shutdown_event: Optional[ShutdownEvent] = None


class SafetyManager:
    """Single authority for safety decisions between GUI and motor control."""

    def __init__(
        self,
        watchdog: Optional[Watchdog] = None,
        emergency_stop: Optional[EmergencyStop] = None,
        shutdown_sequence: Optional[ShutdownSequence] = None,
    ):
        self.watchdog = watchdog or Watchdog()
        self.emergency_stop = emergency_stop or EmergencyStop()
        self.shutdown_sequence = shutdown_sequence or ShutdownSequence()

    def evaluate(self, telemetry: Dict[str, Any]) -> SafetyDecision:
        telemetry_age = telemetry.get('telemetry_age_seconds')
        watchdog_result = self.watchdog.evaluate(telemetry_age)
        if watchdog_result.tripped:
            return self._stop_decision(watchdog_result.reason or 'watchdog:tripped')

        estop_result = self.emergency_stop.evaluate(telemetry)
        if estop_result.should_stop:
            return self._stop_decision(estop_result.reason or 'emergency_stop:tripped')

        return SafetyDecision(healthy=True, should_stop_motor=False)

    def _stop_decision(self, reason: str) -> SafetyDecision:
        event = self.shutdown_sequence.build(reason=reason)
        return SafetyDecision(
            healthy=False,
            should_stop_motor=True,
            reason=reason,
            shutdown_event=event,
        )
