import threading
import time
from app.control.vesc_controller import VESCController


class MotorController:
    """Hardware abstraction preserving placeholder simulation behavior."""

    def __init__(self, settings: dict):
        self.settings = settings
        self.mode = settings.get('motor_mode', 'placeholder')
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self.current_level = None
        self.vesc = VESCController(port=settings.get('vesc_port', '/dev/ttyUSB0'))

    def start(self, level):
        with self._lock:
            self.current_level = level
            if not self._running:
                self._running = True
                self._thread = threading.Thread(target=self._run_loop, daemon=True)
                self._thread.start()
        print(f'MotorController: start({level})')

    def stop(self):
        with self._lock:
            self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
            self._thread = None
        self._hw_set_off()
        print('MotorController: stop()')

    def _run_loop(self):
        try:
            while True:
                with self._lock:
                    if not self._running:
                        break
                    level = self.current_level
                self._hw_set_level(level)
                time.sleep(0.25)
        except Exception as exc:
            print(f'⚠️ MotorController loop error: {exc}')
        finally:
            self._hw_set_off()

    def _hw_set_level(self, level):
        if self.mode == 'placeholder':
            print(f'[SIM] Motor set to {level}')
            return
        if self.mode == 'vesc_serial':
            self.vesc.set_current(level)
            return
        print(f'⚠️ Unknown motor mode: {self.mode}')

    def _hw_set_off(self):
        if self.mode == 'placeholder':
            print('[SIM] Motor OFF')
            return
        self.vesc.stop()
