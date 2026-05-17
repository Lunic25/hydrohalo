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
