"""Math utility functions."""

def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value between minimum and maximum."""
    return max(minimum, min(value, maximum))
