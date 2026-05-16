"""Encoder abstraction."""
class Encoder:
    """Read encoder health for safety checks."""
    def is_healthy(self) -> bool:
        """Return whether encoder appears healthy."""
        return True
