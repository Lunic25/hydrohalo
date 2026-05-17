# HydroHalo Modular Architecture

Entrypoint: `python -m app.main`.

## Architecture Diagram

```text
Tkinter GUI (high-level intents only)
  └─> Session/API Layer (start/stop/change resistance)
      └─> ControlLoopController (50Hz default, monotonic scheduling)
          ├─> SystemStateMachine (explicit transitions)
          ├─> WatchdogController (fault detection + latching)
          ├─> Motor HAL command path
          └─> Telemetry source (hardware or simulation)
```

## Control Flow

1. GUI issues only high-level requests (`start session`, `stop session`, `change resistance`).
2. Control loop thread independently reads telemetry and evaluates watchdog safety checks.
3. State transitions are validated through deterministic transition table.
4. If safe and active, control loop commands motor current.
5. Any watchdog trip causes immediate emergency stop and fault latch.

## Safety Model

- Centralized safety limits live in `app/models/safety_status.py`.
- Faults latch until manual reset.
- Emergency stop path is independent of GUI lifecycle.
- Invalid state transitions are refused and logged.

## Simulation Mode

Run the app without hardware by using `FakeTelemetryGenerator` as telemetry source.

Capabilities:
- Simulated encoder movement.
- Simulated resistance loads (via motor level requests).
- Injected controller faults (`inject_fault(code)`).
- Serial-disconnect simulation (`set_connected(False)`).

## Watchdog

Watchdog monitors:
- telemetry timeout
- encoder timeout
- serial disconnect
- excessive current
- motor runaway
- invalid sensor values
- stalled control loop
- thread death

On trip:
1. cut motor current immediately
2. disable further commands
3. log exact reason
4. transition to `EMERGENCY_STOP`
5. require manual reset to clear latched fault

## Real Hardware Integration (VESC + Encoder)

### Wiring and UART setup
- Connect Raspberry Pi UART adapter TX/RX/GND to VESC UART pins (cross TX↔RX, shared GND).
- Set `uart_port` and `uart_baudrate` in settings/config.
- Keep serial timeout short (default 50ms) for fast fault detection/reconnect.

### Telemetry architecture
- `app/hardware/vesc_uart.py`: thread-safe VESC driver abstraction (`connect`, `disconnect`, telemetry, current commands, E-stop).
- `app/hardware/telemetry_manager.py`: monotonic 50Hz poller with jitter and dropped-packet metrics.
- `app/hardware/encoder_tracker.py`: line position/velocity from encoder counts with jump/stall validation.
- `app/hardware/hardware_manager.py`: orchestration layer with line safety watchdog events.

### Encoder calibration
1. Set `encoder_cpr`, `spool_diameter_mm`, and `gear_ratio`.
2. Call zero calibration before a run (`reset_zero`).
3. Verify measured extension against tape distance and tune spool diameter effective value.

### Safety and testing mode
- Hardware testing mode limits motor current and keeps conservative control behavior.
- Line safety checks include over-extension, unsafe retract distance, rapid acceleration, slack, and encoder stalls.
- On comms failure/disconnect, motor commands fail safe and connection is dropped.

### Troubleshooting
- No telemetry: verify UART port permissions and cable orientation.
- Packet drops/jitter spikes: reduce CPU load and check power integrity/noise.
- Encoder stalls: inspect encoder wiring and CPR configuration.
- Unexpected safety trips: check spool diameter/gear ratio calibration and line routing.

### Bench testing procedure (Raspberry Pi)
1. Start in simulation mode to validate control loop behavior.
2. Enable hardware testing mode and low current limits.
3. Observe telemetry statistics and watchdog events while incrementally increasing load.
4. Validate emergency stop latency and packet-drop behavior.

## Raspberry Pi Touchscreen Kiosk Deployment

### Startup flow
1. Raspberry Pi boots to graphical target.
2. `hydrohalo.service` starts automatically.
3. HydroHalo initializes logging/config in `app/main.py`.
4. App applies safe startup policy (IDLE + motor stop).
5. Splash screen displays centered logo on black background for ~2.5 seconds.
6. Main fullscreen touchscreen GUI appears.

### Production mode behavior
`AppSettings.production_mode=True` enforces kiosk constraints:
- fullscreen forced
- Escape key ignored
- cursor hidden (if enabled)
- simulation mode disabled unless `allow_simulation_in_production=True`

### Raspberry Pi setup
1. Copy repo to `/opt/hydrohalo`.
2. Run installer:
   ```bash
   sudo bash deploy/install.sh
   ```
3. Verify service:
   ```bash
   systemctl status hydrohalo.service
   ```
4. Reboot and confirm kiosk auto-launch.

### Touchscreen optimization notes
- UI targets are enlarged for 5-inch display use.
- Primary controls are large, high-contrast buttons.
- Layout is optimized for landscape orientation.
- Cursor hiding is supported for kiosk feel.

### Troubleshooting
- Service logs:
  - `/var/log/hydrohalo/hydrohalo.out.log`
  - `/var/log/hydrohalo/hydrohalo.err.log`
- If hardware is unavailable in production mode, HydroHalo stays fail-safe and motor output remains disabled.
- If GUI crashes, systemd restarts the app automatically.
