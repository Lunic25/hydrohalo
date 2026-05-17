from app.controllers.state_machine import SystemState, SystemStateMachine


def test_valid_transitions():
    sm = SystemStateMachine()
    assert sm.transition_to(SystemState.READY, "prep")
    assert sm.transition_to(SystemState.ACTIVE_RESISTANCE, "start")
    assert sm.get_state() == SystemState.ACTIVE_RESISTANCE


def test_invalid_transition_refused():
    sm = SystemStateMachine()
    assert not sm.transition_to(SystemState.ACTIVE_RESISTANCE, "invalid")
    assert sm.get_state() == SystemState.IDLE
