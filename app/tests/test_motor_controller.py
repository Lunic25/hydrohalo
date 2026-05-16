from app.controllers.motor_controller import MotorController
from app.controllers.safety_controller import SafetyController
from app.hardware.vesc_interface import VESCInterface

def test_motor_controller_start_stop():
    vesc = VESCInterface('/dev/null', simulation_mode=True)
    controller = MotorController(vesc=vesc, safety=SafetyController())
    controller.start('Low')
    controller.stop()
