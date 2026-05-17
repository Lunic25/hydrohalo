"""Typed runtime settings models."""
from dataclasses import dataclass


@dataclass
class AppSettings:
    """Container for persisted HydroHalo runtime settings."""

    use_gpio: bool = False
    use_sound: bool = True
    default_duration: int = 10
    motor_mode: str = "simulation"
    vesc_port: str = "/dev/ttyUSB0"
    simulation_mode: bool = True

    uart_port: str = "/dev/ttyUSB0"
    uart_baudrate: int = 115200
    encoder_cpr: int = 1024
    spool_diameter_mm: float = 60.0
    gear_ratio: float = 1.0
    max_line_length_m: float = 40.0
    max_safe_current_a: float = 12.0
    hardware_testing_mode: bool = True

    production_mode: bool = True
    hide_cursor: bool = True
    splash_duration_ms: int = 2500
    allow_simulation_in_production: bool = False
