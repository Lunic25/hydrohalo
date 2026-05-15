"""Compatibility wrapper for refactored controller classes."""

from app.control.motor_controller import MotorController
from app.control.vesc_controller import VESCController

__all__ = ['MotorController', 'VESCController']
