"""Independent safety controller."""
from __future__ import annotations
from app.safety.safety_manager import SafetyManager, SafetyDecision

class SafetyController:
    """Orchestrates safety decisions independent of GUI state."""
    def __init__(self, manager: SafetyManager | None = None):
        self.manager = manager or SafetyManager()

    def evaluate(self, telemetry: dict) -> SafetyDecision:
        """Evaluate telemetry and return safety decision."""
        return self.manager.evaluate(telemetry)
