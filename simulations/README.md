# Simulation Engine

The backend exposes `POST /api/simulations/run` for scenario simulation.

Supported current scenarios:

- equipment_failure
- gas_leak
- fire
- permit_conflict
- worker_evacuation
- hazard_propagation
- emergency_response

The first implementation uses real risk, zone, telemetry, permit, and incident-derived context from the platform database. It does not fabricate production telemetry.

