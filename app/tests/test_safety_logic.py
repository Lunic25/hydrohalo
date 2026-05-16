from app.controllers.safety_controller import SafetyController

def test_safety_stops_on_zero_force():
    decision = SafetyController().evaluate({'pull_force': 0, 'telemetry_age_seconds': 0})
    assert decision.should_stop_motor
