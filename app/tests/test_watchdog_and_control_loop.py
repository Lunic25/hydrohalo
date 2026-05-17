import time

from app.controllers.control_loop import ControlLoopController
from app.controllers.state_machine import SystemState
from app.controllers.watchdog_controller import WatchdogController
from app.models.telemetry import FakeTelemetryGenerator


class DummyMotor:
    def __init__(self):
        self.currents = []
        self.stopped = False
        self.emergency = False

    def set_current_by_level(self, level: str) -> None:
        self.currents.append(level)

    def stop(self):
        self.stopped = True

    def emergency_shutdown(self):
        self.emergency = True


def test_watchdog_trips_on_excessive_current():
    wd = WatchdogController()
    t = FakeTelemetryGenerator().read_telemetry()
    t.current = 99.0
    result = wd.evaluate(t, serial_connected=True, loop_alive=True, control_loop_age_ms=10.0, control_thread_alive=True)
    assert result.tripped
    assert result.reason == "excessive_current"


def test_control_loop_emergency_stop_and_latch():
    motor = DummyMotor()
    telemetry = FakeTelemetryGenerator()
    telemetry.inject_fault(7)
    loop = ControlLoopController(motor, telemetry, frequency_hz=30)
    loop.request_start_session()
    loop.start()
    time.sleep(0.08)
    loop.stop()
    assert motor.emergency
    assert loop.watchdog.status.fault_latched
    assert loop.state_machine.get_state() == SystemState.EMERGENCY_STOP


def test_control_loop_timing_stats_populate():
    motor = DummyMotor()
    telemetry = FakeTelemetryGenerator()
    loop = ControlLoopController(motor, telemetry, frequency_hz=50)
    loop.request_start_session()
    loop.start()
    time.sleep(0.12)
    loop.stop()
    assert loop.stats.cycles > 0
    assert loop.stats.max_jitter_ms >= 0.0
