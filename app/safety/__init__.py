"""Safety system layer for HydroHalo."""

from app.safety.emergency_stop import EmergencyStop, EmergencyStopResult
from app.safety.safety_manager import SafetyDecision, SafetyManager
from app.safety.shutdown_sequence import ShutdownEvent, ShutdownSequence
from app.safety.watchdog import Watchdog, WatchdogResult

__all__ = [
    'EmergencyStop',
    'EmergencyStopResult',
    'SafetyDecision',
    'SafetyManager',
    'ShutdownEvent',
    'ShutdownSequence',
    'Watchdog',
    'WatchdogResult',
]
