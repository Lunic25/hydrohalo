import time
from app.hardware.telemetry_manager import TelemetryManager
from app.hardware.vesc_uart import VESCUartConfig, VESCUartDriver


def test_telemetry_runs_near_target_rate():
    d = VESCUartDriver(VESCUartConfig(simulation_mode=True))
    d.connect()
    tm = TelemetryManager(d, target_hz=50.0)
    tm.start()
    time.sleep(0.25)
    tm.stop()
    s = tm.stats()
    assert s.samples >= 8
