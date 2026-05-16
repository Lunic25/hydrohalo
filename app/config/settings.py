"""Typed runtime settings models."""
from dataclasses import dataclass

@dataclass
class AppSettings:
    """Container for persisted HydroHalo runtime settings."""
    use_gpio: bool = False
    use_sound: bool = True
    default_duration: int = 10
    motor_mode: str = 'simulation'
    vesc_port: str = '/dev/ttyUSB0'
    simulation_mode: bool = True
