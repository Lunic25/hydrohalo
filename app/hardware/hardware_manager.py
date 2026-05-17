"""Central orchestration for hardware lifecycle and safety checks."""
from __future__ import annotations

from dataclasses import dataclass
import time
from app.hardware.vesc_uart import VESCUartDriver, VESCUartConfig
from app.hardware.telemetry_manager import TelemetryManager
from app.hardware.encoder_tracker import EncoderTracker, EncoderConfig


@dataclass(slots=True)
class HardwareConfig:
    simulation_mode: bool = True
    uart_port: str = "/dev/ttyUSB0"
    uart_baudrate: int = 115200
    encoder_cpr: int = 1024
    spool_diameter_mm: float = 60.0
    gear_ratio: float = 1.0
    max_line_length_m: float = 40.0
    min_retract_distance_m: float = 0.2
    rapid_accel_mps2: float = 4.0
    sudden_slack_mps: float = -2.0


class HardwareManager:
    def __init__(self, config: HardwareConfig):
        self.config = config
        self.vesc = VESCUartDriver(VESCUartConfig(
            uart_port=config.uart_port,
            uart_baudrate=config.uart_baudrate,
            simulation_mode=config.simulation_mode,
        ))
        self.telemetry = TelemetryManager(self.vesc, target_hz=50.0)
        self.encoder = EncoderTracker(EncoderConfig(
            encoder_cpr=config.encoder_cpr,
            spool_diameter_mm=config.spool_diameter_mm,
            gear_ratio=config.gear_ratio,
        ))
        self.watchdog_events: list[str] = []
        self._last_v = 0.0
        self._last_ts = time.monotonic()

    def initialize(self) -> bool:
        ok = self.vesc.connect()
        self.telemetry.start()
        return ok

    def shutdown(self) -> None:
        self.telemetry.stop()
        self.vesc.emergency_stop()
        self.vesc.disconnect()

    def update_encoder_counts(self, counts: int, timestamp: float | None = None) -> None:
        prev = self.encoder.get_position_m()
        self.encoder.update(counts, timestamp=timestamp)
        pos = self.encoder.get_position_m()
        if not self.encoder.validate_reading(prev, pos):
            self.watchdog_events.append("encoder_impossible_jump")
        if pos > self.config.max_line_length_m:
            self.watchdog_events.append("line_over_extension")
        if pos < self.config.min_retract_distance_m:
            self.watchdog_events.append("unsafe_retract_distance")
        now = time.monotonic()
        dt = max(1e-6, now - self._last_ts)
        v = self.encoder.get_velocity_mps()
        accel = (v - self._last_v) / dt
        if abs(accel) > self.config.rapid_accel_mps2:
            self.watchdog_events.append("rapid_acceleration")
        if v < self.config.sudden_slack_mps:
            self.watchdog_events.append("sudden_slack")
        if self.encoder.is_stalled():
            self.watchdog_events.append("encoder_stall")
        self._last_v = v
        self._last_ts = now

    def aggregate(self) -> dict:
        return {
            "connected": self.vesc.is_connected(),
            "telemetry": self.telemetry.get_latest(),
            "telemetry_stats": self.telemetry.stats(),
            "position_m": self.encoder.get_position_m(),
            "velocity_mps": self.encoder.get_velocity_mps(),
            "watchdog_events": list(self.watchdog_events),
        }



def run_terminal_monitor(manager: HardwareManager, duration_s: float = 5.0, refresh_hz: float = 5.0) -> None:
    """Simple terminal diagnostics monitor for bench testing."""
    period = 1.0 / refresh_hz
    end = time.monotonic() + duration_s
    while time.monotonic() < end:
        snapshot = manager.aggregate()
        print({
            "connected": snapshot["connected"],
            "watchdog_events": snapshot["watchdog_events"][-3:],
            "position_m": round(snapshot["position_m"], 3),
            "velocity_mps": round(snapshot["velocity_mps"], 3),
            "telemetry": snapshot["telemetry"],
            "telemetry_stats": snapshot["telemetry_stats"],
        })
        time.sleep(period)
