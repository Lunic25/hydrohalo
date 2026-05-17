import time
from app.hardware.vesc_uart import VESCUartConfig, VESCUartDriver


def test_emergency_stop_latency_under_100ms():
    d = VESCUartDriver(VESCUartConfig(simulation_mode=True))
    d.connect()
    detect_ts = time.monotonic()
    d.emergency_stop()
    confirm_ts = time.monotonic()
    total_ms = (confirm_ts - detect_ts) * 1000.0
    assert total_ms < 100.0
