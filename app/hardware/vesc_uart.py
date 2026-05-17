"""Thread-safe VESC UART abstraction with simulation fallback."""
from __future__ import annotations

from dataclasses import dataclass, field
import threading
import time
from typing import Any, Optional, Protocol


class VescBackend(Protocol):
    def set_current(self, current: float) -> None: ...
    def get_measurements(self) -> Any: ...
    def stop_heartbeat(self) -> None: ...
    def __enter__(self) -> "VescBackend": ...
    def __exit__(self, exc_type, exc, tb) -> None: ...


@dataclass(slots=True)
class VescTelemetry:
    timestamp: float
    motor_current: float = 0.0
    input_current: float = 0.0
    rpm: float = 0.0
    duty_cycle: float = 0.0
    mosfet_temp_c: float = 0.0
    motor_temp_c: float = 0.0
    input_voltage: float = 0.0
    fault_code: int = 0
    tachometer: int = 0
    tachometer_abs: int = 0
    packet_dropped: bool = False


@dataclass(slots=True)
class VESCUartConfig:
    uart_port: str = "/dev/ttyUSB0"
    uart_baudrate: int = 115200
    timeout_s: float = 0.05
    heartbeat_s: float = 0.2
    max_safe_current_a: float = 12.0
    simulation_mode: bool = True
    testing_mode: bool = True
    testing_max_current_a: float = 3.0


class VESCUartDriver:
    def __init__(self, config: VESCUartConfig, logger=None, backend_factory=None):
        self.config = config
        self.logger = logger
        self._backend_factory = backend_factory
        self._backend: Optional[VescBackend] = None
        self._lock = threading.RLock()
        self._connected = False
        self._last_telemetry = VescTelemetry(timestamp=time.monotonic())
        self._last_heartbeat = 0.0

    def connect(self) -> bool:
        with self._lock:
            if self._connected:
                return True
            if self.config.simulation_mode:
                self._connected = True
                return True
            try:
                if self._backend_factory is None:
                    from pyvesc import VESC
                    self._backend = VESC(serial_port=self.config.uart_port, baudrate=self.config.uart_baudrate, timeout=self.config.timeout_s)
                else:
                    self._backend = self._backend_factory()
                self._connected = True
                return True
            except Exception:
                self._connected = False
                return False

    def disconnect(self) -> None:
        with self._lock:
            self._connected = False
            if self._backend is not None:
                try:
                    self._backend.stop_heartbeat()
                except Exception:
                    pass
                self._backend = None

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def _clamp_current(self, current_a: float) -> float:
        limit = self.config.testing_max_current_a if self.config.testing_mode else self.config.max_safe_current_a
        return max(-limit, min(limit, current_a))

    def set_motor_current(self, current_a: float) -> bool:
        with self._lock:
            if not self._connected:
                return False
            current_a = self._clamp_current(current_a)
            if self.config.simulation_mode or self._backend is None:
                return True
            try:
                self._backend.set_current(current_a)
                self._last_heartbeat = time.monotonic()
                return True
            except Exception:
                self.disconnect()
                return False

    def stop_motor(self) -> None:
        self.set_motor_current(0.0)

    def emergency_stop(self) -> None:
        self.stop_motor()

    def get_telemetry(self) -> VescTelemetry:
        with self._lock:
            now = time.monotonic()
            if not self._connected:
                return VescTelemetry(timestamp=now, packet_dropped=True)
            if self.config.simulation_mode or self._backend is None:
                self._last_telemetry = VescTelemetry(timestamp=now)
                return self._last_telemetry
            try:
                m = self._backend.get_measurements()
                t = VescTelemetry(
                    timestamp=now,
                    motor_current=float(getattr(m, "avg_motor_current", 0.0)),
                    input_current=float(getattr(m, "avg_input_current", 0.0)),
                    rpm=float(getattr(m, "rpm", 0.0)),
                    duty_cycle=float(getattr(m, "duty_cycle_now", 0.0)),
                    mosfet_temp_c=float(getattr(m, "temp_fet", 0.0)),
                    motor_temp_c=float(getattr(m, "temp_motor", 0.0)),
                    input_voltage=float(getattr(m, "v_in", 0.0)),
                    fault_code=int(getattr(m, "fault_code", 0) or 0),
                    tachometer=int(getattr(m, "tachometer", 0) or 0),
                    tachometer_abs=int(getattr(m, "tachometer_abs", 0) or 0),
                )
                self._last_telemetry = t
                return t
            except Exception:
                self.disconnect()
                return VescTelemetry(timestamp=now, packet_dropped=True)
