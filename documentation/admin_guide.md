# Administrator Guide

## Environment

- `APP_SECRET`: signing secret for access tokens.
- `DEMO_ADMIN_PASSWORD`: initial admin password.
- `SAFETY_DB_PATH`: SQLite database path.
- `GROQ_API_KEY`: optional external LLM key. The application does not require or store it.

## Data Refresh

Run these in order:

```bash
python3 scripts/data_engineering/validate_datasets.py
python3 scripts/data_engineering/build_processed_datasets.py
rm -f backend/safety_platform.db
python3 rag/build_rag_index.py
python3 knowledge_graph/build_graph.py
python3 ai/training/train_models.py
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

## Audit

Admin users can view `/api/admin/audit-logs`. Safety-critical agent runs, permit reviews, reports, logins, and simulations are recorded.

