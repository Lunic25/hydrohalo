"""Structured logging facilities."""
from __future__ import annotations
import logging
from app.config.constants import LOG_DIR

def configure_logging() -> logging.Logger:
    """Configure and return the application logger."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger('hydrohalo')
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    fh = logging.FileHandler(LOG_DIR / 'hydrohalo.log')
    fh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger
