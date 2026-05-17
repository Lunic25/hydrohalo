from app.hardware.encoder_tracker import EncoderConfig, EncoderTracker


def test_position_and_velocity():
    t = EncoderTracker(EncoderConfig(encoder_cpr=1000, spool_diameter_mm=100, gear_ratio=1.0))
    t.update(0, timestamp=0.0)
    t.update(1000, timestamp=1.0)
    assert t.get_position_m() > 0.31
    assert t.get_velocity_mps() > 0.31


def test_impossible_jump_detection():
    t = EncoderTracker(EncoderConfig(impossible_jump_m=0.1))
    assert t.validate_reading(0.0, 0.05)
    assert not t.validate_reading(0.0, 0.5)
