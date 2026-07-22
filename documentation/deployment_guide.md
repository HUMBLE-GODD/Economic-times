# Deployment Guide

## Local

```bash
python3 rag/build_rag_index.py
python3 knowledge_graph/build_graph.py
python3 ai/training/train_models.py
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

Default demo account:

- Email: `admin@industrial.local`
- Password: `SafetyDemo!2026`

Set `APP_SECRET` and `DEMO_ADMIN_PASSWORD` in production.

## Docker

```bash
cd deployment
docker compose up --build
```

## Production Notes

- Replace SQLite with Postgres and TimescaleDB.
- Move report/model artifacts to object storage.
- Use a real identity provider for SSO/MFA.
- Rotate all secrets and never hardcode API keys.
- Add backups for the database and generated reports.
- Review licenses before commercial use of UCI datasets.

