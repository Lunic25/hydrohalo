"""Telemetry polling service."""
class TelemetryService:
    """Provides unified telemetry polling for controllers."""
    def __init__(self, vesc_interface):
        self.vesc_interface = vesc_interface

    def read(self) -> dict:
        """Read telemetry via hardware interface."""
        return self.vesc_interface.read_telemetry()
