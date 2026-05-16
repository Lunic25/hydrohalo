# HydroHalo Modular Architecture

Entrypoint: `python -m app.main`.

- `config/`: constants and typed settings.
- `controllers/`: business logic orchestration.
- `hardware/`: hardware abstraction layer (VESC/GPIO/sensors).
- `gui/`: Tkinter views/pages only.
- `services/`: cross-cutting services (logging/settings/telemetry).
- `models/`: simple data models.
- `utils/`: generic helpers.
- `tests/`: baseline tests.

Simulation mode is controlled by `simulation_mode` in settings.
