"""50Hz telemetry poller with jitter and drop accounting."""
from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from collections import deque


@dataclass(slots=True)
class TelemetryStats:
    drops: int = 0
    samples: int = 0
    avg_jitter_ms: float = 0.0
    max_jitter_ms: float = 0.0


class TelemetryManager:
    def __init__(self, vesc_driver, target_hz: float = 50.0):
        self.vesc_driver = vesc_driver
        self.target_hz = target_hz
        self._period = 1.0 / target_hz
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._latest = None
        self._jitter = deque(maxlen=500)
        self._drops = 0

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _loop(self) -> None:
        nxt = time.monotonic()
        while self._running:
            now = time.monotonic()
            if now < nxt:
                time.sleep(nxt - now)
            actual = time.monotonic()
            jitter_ms = abs((actual - nxt) * 1000.0)
            self._jitter.append(jitter_ms)
            t = self.vesc_driver.get_telemetry()
            if getattr(t, "packet_dropped", False):
                self._drops += 1
            with self._lock:
                self._latest = t
            nxt += self._period

    def get_latest(self):
        with self._lock:
            return self._latest

    def stats(self) -> TelemetryStats:
        samples = len(self._jitter)
        avg = sum(self._jitter) / samples if samples else 0.0
        return TelemetryStats(drops=self._drops, samples=samples, avg_jitter_ms=avg, max_jitter_ms=max(self._jitter) if samples else 0.0)
