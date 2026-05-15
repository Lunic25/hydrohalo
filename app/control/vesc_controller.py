"""VESC communication placeholder that reuses existing pyvesc-style logic."""


class VESCController:
    def __init__(self, port='/dev/ttyUSB0'):
        self.port = port
        self.vesc = None
        try:
            from pyvesc import VESC

            self.vesc = VESC(serial_port=port)
            print(f'✅ Connected to VESC on {port}')
        except Exception as exc:
            print(f'⚠️ VESC unavailable, running in simulation mode: {exc}')

    def set_current(self, current: float) -> None:
        if not self.vesc:
            print(f'[SIM] VESC set_current({current})')
            return
        try:
            self.vesc.set_current(current)
            print(f'Applied {current}A torque resistance')
        except Exception as exc:
            print(f'⚠️ VESC set_current failed: {exc}')

    def stop(self) -> None:
        self.set_current(0)
