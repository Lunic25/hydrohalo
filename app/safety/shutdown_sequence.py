from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass(frozen=True)
class ShutdownEvent:
    reason: str
    ramp_steps: int


class ShutdownSequence:
    """Represents an orderly safety shutdown plan.

    This class intentionally avoids direct hardware control and returns a shutdown
    plan/callback sequence to be executed by a motor-control adapter later.
    """

    def __init__(self, ramp_steps: int = 3):
        self.ramp_steps = max(1, int(ramp_steps))

    def build(self, reason: str, stop_callback: Optional[Callable[[], None]] = None) -> ShutdownEvent:
        if stop_callback is not None:
            for _ in range(self.ramp_steps):
                stop_callback()
            stop_callback()
        return ShutdownEvent(reason=reason, ramp_steps=self.ramp_steps)

    @staticmethod
    def format_log_message(event: ShutdownEvent) -> str:
        return f'shutdown | reason={event.reason} | ramp_steps={event.ramp_steps}'
