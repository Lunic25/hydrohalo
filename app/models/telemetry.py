from dataclasses import dataclass
import time


@dataclass(slots=True)
class Telemetry:
    timestamp: float
    current: float
    rpm: float
    duty_cycle: float
    motor_temp: float
    controller_temp: float
    voltage: float
    encoder_position: float
    line_length_m: float
    fault_code: int = 0


class FakeTelemetryGenerator:
    """Simulation telemetry source with injectable faults."""

    def __init__(self) -> None:
        self.connected = True
        self._position = 0.0
        self._rpm = 300.0
        self._fault_code = 0

    def inject_fault(self, fault_code: int) -> None:
        self._fault_code = fault_code

    def set_connected(self, connected: bool) -> None:
        self.connected = connected

    def read_telemetry(self) -> Telemetry:
        self._position += self._rpm / 60.0 * 0.02
        line_length = max(0.0, self._position * 0.01)
        return Telemetry(
            timestamp=time.monotonic(),
            current=4.0,
            rpm=self._rpm,
            duty_cycle=0.3,
            motor_temp=42.0,
            controller_temp=38.0,
            voltage=48.0,
            encoder_position=self._position,
            line_length_m=line_length,
            fault_code=self._fault_code,
        )
