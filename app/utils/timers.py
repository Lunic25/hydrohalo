"""Timing helpers."""
from time import monotonic

def now() -> float:
    """Return monotonic timestamp."""
    return monotonic()
