from dataclasses import dataclass
from typing import Optional

@dataclass
class Telemetry:
    """Current telemetry snapshot from hardware/simulation."""
    motor_rpm: float = 0.0
    pull_force: Optional[float] = 1.0
    encoder_ok: bool = True
