from app.hardware.vesc_uart import VESCUartConfig, VESCUartDriver


def test_simulation_connect_and_disconnect():
    d = VESCUartDriver(VESCUartConfig(simulation_mode=True))
    assert d.connect() is True
    assert d.is_connected() is True
    d.disconnect()
    assert d.is_connected() is False


def test_current_clamped_in_testing_mode():
    d = VESCUartDriver(VESCUartConfig(simulation_mode=True, testing_mode=True, testing_max_current_a=2.0))
    d.connect()
    assert d.set_motor_current(10.0) is True
