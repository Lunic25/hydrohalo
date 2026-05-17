"""Deterministic control state machine for HydroHalo."""
from __future__ import annotations

from enum import Enum
from threading import RLock
import logging


class SystemState(Enum):
    IDLE = "IDLE"
    READY = "READY"
    ACTIVE_RESISTANCE = "ACTIVE_RESISTANCE"
    REELING_IN = "REELING_IN"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    FAULT = "FAULT"
    SHUTDOWN = "SHUTDOWN"


_ALLOWED_TRANSITIONS: dict[SystemState, set[SystemState]] = {
    SystemState.IDLE: {SystemState.READY, SystemState.SHUTDOWN},
    SystemState.READY: {SystemState.ACTIVE_RESISTANCE, SystemState.IDLE, SystemState.SHUTDOWN},
    SystemState.ACTIVE_RESISTANCE: {
        SystemState.REELING_IN,
        SystemState.READY,
        SystemState.EMERGENCY_STOP,
        SystemState.FAULT,
    },
    SystemState.REELING_IN: {
        SystemState.READY,
        SystemState.EMERGENCY_STOP,
        SystemState.FAULT,
    },
    SystemState.EMERGENCY_STOP: {SystemState.FAULT, SystemState.IDLE},
    SystemState.FAULT: {SystemState.IDLE, SystemState.SHUTDOWN},
    SystemState.SHUTDOWN: set(),
}


class SystemStateMachine:
    """Thread-safe deterministic state machine with explicit transitions."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._state = SystemState.IDLE
        self._lock = RLock()
        self._logger = logger or logging.getLogger("hydrohalo.state_machine")

    def get_state(self) -> SystemState:
        with self._lock:
            return self._state

    def can_transition(self, target: SystemState) -> bool:
        with self._lock:
            return target in _ALLOWED_TRANSITIONS[self._state]

    def transition_to(self, target: SystemState, reason: str = "") -> bool:
        with self._lock:
            source = self._state
            if target == source:
                return True
            if target not in _ALLOWED_TRANSITIONS[source]:
                self._logger.warning(
                    "invalid_transition subsystem=state_machine from_state=%s to_state=%s reason=%s",
                    source.value,
                    target.value,
                    reason,
                )
                return False
            self._state = target
            self._logger.info(
                "state_transition subsystem=state_machine from_state=%s to_state=%s reason=%s",
                source.value,
                target.value,
                reason,
            )
            return True
