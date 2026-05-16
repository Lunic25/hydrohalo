"""Thread utility helpers."""
import threading

def make_daemon_thread(target, name: str) -> threading.Thread:
    """Create a daemon thread for background work."""
    return threading.Thread(target=target, name=name, daemon=True)
