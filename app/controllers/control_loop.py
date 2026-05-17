"""High-frequency hardware control loop."""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

from app.controllers.state_machine import SystemState, SystemStateMachine
from app.controllers.watchdog_controller import WatchdogController
from app.models.telemetry import Telemetry


@dataclass(slots=True)
class ControlLoopStats:
    cycles: int = 0
    overruns: int = 0
    max_jitter_ms: float = 0.0


class ControlLoopController:
    def __init__(self, motor, telemetry_source, *, frequency_hz: float = 50.0, logger: logging.Logger | None = None) -> None:
        self.motor = motor
        self.telemetry_source = telemetry_source
        self.frequency_hz = frequency_hz
        self.logger = logger or logging.getLogger("hydrohalo.control_loop")
        self.state_machine = SystemStateMachine(logger=self.logger)
        self.watchdog = WatchdogController(logger=self.logger)
        self.stats = ControlLoopStats()
        self._shutdown = threading.Event()
        self._thread: threading.Thread | None = None
        self._requested_level = "Low"
        self._commands_enabled = True
        self._last_cycle_start = time.monotonic()

    def request_start_session(self) -> None:
        self.state_machine.transition_to(SystemState.READY, "start_request")
        self.state_machine.transition_to(SystemState.ACTIVE_RESISTANCE, "start_request")

    def request_stop_session(self) -> None:
        self.state_machine.transition_to(SystemState.REELING_IN, "stop_request")
        self.state_machine.transition_to(SystemState.READY, "stop_request")

    def request_resistance_level(self, level: str) -> None:
        self._requested_level = level

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._shutdown.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="hydrohalo-control-loop")
        self._thread.start()

    def stop(self) -> None:
        self._shutdown.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self.motor.stop()

    def manual_reset(self) -> None:
        self.watchdog.status.clear()
        self._commands_enabled = True
        self.state_machine.transition_to(SystemState.IDLE, "manual_reset")

    def emergency_stop(self, reason: str, controlled_reel_in: bool = False) -> None:
        self.motor.emergency_shutdown()
        self._commands_enabled = False
        self.state_machine.transition_to(SystemState.EMERGENCY_STOP, reason)
        self.logger.critical("emergency_stop subsystem=control_loop reason=%s", reason)
        if controlled_reel_in:
            self.state_machine.transition_to(SystemState.REELING_IN, "controlled_reel_in")

    def _run(self) -> None:
        period = 1.0 / self.frequency_hz
        next_tick = time.monotonic()
        while not self._shutdown.is_set():
            cycle_start = time.monotonic()
            telemetry: Telemetry = self.telemetry_source.read_telemetry()
            wd = self.watchdog.evaluate(
                telemetry,
                serial_connected=getattr(self.telemetry_source, "connected", True),
                loop_alive=True,
                control_loop_age_ms=(cycle_start - self._last_cycle_start) * 1000.0,
                control_thread_alive=threading.current_thread().is_alive(),
            )
            self._last_cycle_start = cycle_start
            if wd.tripped:
                self.emergency_stop(wd.reason)
            elif self._commands_enabled and self.state_machine.get_state() == SystemState.ACTIVE_RESISTANCE:
                self.motor.set_current_by_level(self._requested_level)

            elapsed = time.monotonic() - cycle_start
            jitter_ms = abs((elapsed - period) * 1000.0)
            self.stats.max_jitter_ms = max(self.stats.max_jitter_ms, jitter_ms)
            self.stats.cycles += 1
            if elapsed > period:
                self.stats.overruns += 1
                self.logger.warning("loop_overrun subsystem=control_loop elapsed_ms=%.2f", elapsed * 1000.0)

            next_tick += period
            sleep_s = next_tick - time.monotonic()
            if sleep_s > 0:
                time.sleep(sleep_s)
