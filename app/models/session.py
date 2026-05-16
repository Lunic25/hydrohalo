from dataclasses import dataclass

@dataclass
class Session:
    """Represents a motor resistance session."""
    level: str
    duration_seconds: int
