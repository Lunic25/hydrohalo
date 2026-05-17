"""Encoder-based spool tracking and safety validation."""
from __future__ import annotations

from dataclasses import dataclass
import math
import time


@dataclass(slots=True)
class EncoderConfig:
    encoder_cpr: int = 1024
    spool_diameter_mm: float = 60.0
    gear_ratio: float = 1.0
    invert_direction: bool = False
    impossible_jump_m: float = 0.5
    stall_timeout_s: float = 1.0


class EncoderTracker:
    def __init__(self, config: EncoderConfig):
        self.config = config
        self._zero_counts = 0
        self._last_counts = 0
        self._last_ts = time.monotonic()
        self._last_pos = 0.0
        self._velocity = 0.0
        self._stall = False

    def _counts_to_meters(self, counts: int) -> float:
        revs = counts / max(1, self.config.encoder_cpr)
        shaft_revs = revs / max(1e-9, self.config.gear_ratio)
        meters_per_rev = math.pi * (self.config.spool_diameter_mm / 1000.0)
        pos = shaft_revs * meters_per_rev
        return -pos if self.config.invert_direction else pos

    def update(self, counts: int, timestamp: float | None = None) -> None:
        ts = time.monotonic() if timestamp is None else timestamp
        rel_counts = counts - self._zero_counts
        pos = self._counts_to_meters(rel_counts)
        dt = max(1e-6, ts - self._last_ts)
        self._velocity = (pos - self._last_pos) / dt
        self._stall = abs(counts - self._last_counts) == 0 and (ts - self._last_ts) >= self.config.stall_timeout_s
        self._last_counts = counts
        self._last_pos = pos
        self._last_ts = ts

    def get_position_m(self) -> float:
        return self._last_pos

    def get_velocity_mps(self) -> float:
        return self._velocity

    def reset_zero(self, counts: int = 0) -> None:
        self._zero_counts = counts
        self._last_counts = counts
        self._last_pos = 0.0

    def validate_reading(self, prev_position_m: float, position_m: float) -> bool:
        return abs(position_m - prev_position_m) <= self.config.impossible_jump_m

    def is_stalled(self) -> bool:
        return self._stall
