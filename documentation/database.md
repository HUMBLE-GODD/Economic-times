# Database Documentation

Schema migration: `backend/migrations/001_init.sql`.

Main entities:

- `organizations`
- `plants`
- `departments`
- `zones`
- `users`
- `refresh_tokens`
- `equipment`
- `sensors`
- `workers`
- `telemetry`
- `maintenance_events`
- `permits`
- `incidents`
- `hazards`
- `risk_events`
- `compliance_records`
- `documents`
- `kg_nodes`
- `kg_edges`
- `predictions`
- `audit_logs`
- `notifications`
- `simulations`
- `reports_generated`

Indexes are included for incident geospatial lookups, risk ordering, telemetry time, equipment priority, permit status, compliance status, and graph traversal.

