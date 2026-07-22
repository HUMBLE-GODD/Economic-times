# API Documentation

Base URL: `http://127.0.0.1:8000`

Authenticate with:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@industrial.local","password":"SafetyDemo!2026"}'
```

Use the returned `access_token` as `Authorization: Bearer <token>`.

## Core Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Runtime health |
| `/api/auth/login` | POST | Login |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Current user |
| `/api/mission-control` | GET | KPIs, alerts, top risks |
| `/api/plants` | GET | Plants and zones |
| `/api/assets` | GET | Equipment health |
| `/api/workers` | GET | Worker role risk profiles |
| `/api/maintenance` | GET | Predictive maintenance events |
| `/api/incidents` | GET | Incident intelligence |
| `/api/risk/compound` | GET | Compound risk score |
| `/api/risk/geospatial` | GET | Incident/zone geospatial risk |
| `/api/permits` | GET | Permit records |
| `/api/permits/review` | POST | Digital permit review |
| `/api/compliance` | GET | Compliance records and documents |
| `/api/knowledge/query` | POST | RAG with evidence |
| `/api/knowledge-graph` | GET | Nodes and relationships |
| `/api/digital-twin` | GET | Digital twin payload |
| `/api/agents` | GET | Agent catalog |
| `/api/agents/{agent_id}/run` | POST | Run specialized agent |
| `/api/models` | GET | Model registry |
| `/api/simulations/run` | POST | Run simulation |
| `/api/reports/generate` | POST | Generate PDF and XLSX |
| `/api/admin/audit-logs` | GET | Audit logs |
| `/api/computer-vision/status` | GET | CV module status |
| `/ws/alerts` | WebSocket | Alert stream |

