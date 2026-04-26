# DPDP PrivacyOps Backend

FastAPI backend foundation for Stage 2 of DPDP PrivacyOps. This service accepts local scanner JSON output, validates the privacy contract, stores scans and findings, and exposes APIs for the future dashboard.

It does not include auth, billing, DSR handling, consent APIs, evidence reports, external integrations, or frontend code.

## Setup

Use Python 3.11+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Environment

Copy `.env.example` and set:

- `DATABASE_URL`: SQLAlchemy database URL. Local Postgres example: `postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp_privacyops`
- `APP_ENV`: `development`, `test`, or `production`
- `CORS_ORIGINS`: comma-separated allowed origins

For quick local development without Postgres, the app defaults to `sqlite:///./dpdp_privacyops_dev.db`.

## Local Postgres

From the repo root:

```bash
docker compose up -d postgres
```

## Migrations

From `backend/`:

```bash
alembic upgrade head
```

Create a future migration:

```bash
alembic revision --autogenerate -m "Describe change"
```

## Run API

From `backend/`:

```bash
python -m uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Run Tests

```bash
pytest
```

Tests use SQLite in-memory for reliability. The models and Alembic migration are kept Postgres-compatible for local Postgres and production later.

## Create Project

```bash
curl -X POST http://127.0.0.1:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Acme",
    "project_name": "Main App",
    "description": "Primary SaaS product"
  }'
```

## Upload Scanner JSON

Scanner output is accepted exactly as JSON from `dpdp-scanner`. The backend rejects payloads where `raw_pii_uploaded` is anything other than `false`.

```bash
dpdp-scanner scan-json \
  --path ../scanner/tests/fixtures/sample_logs.jsonl \
  --output /tmp/findings_logs.json
```

```bash
curl -X POST http://127.0.0.1:8000/projects/<PROJECT_ID>/scans/upload \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/findings_logs.json
```

The response includes:

- scan metadata
- `total_findings`
- counts by risk level
- counts by PII type
- critical and high counts

## Findings APIs

```bash
curl "http://127.0.0.1:8000/projects/<PROJECT_ID>/findings?risk_level=critical"
curl "http://127.0.0.1:8000/projects/<PROJECT_ID>/findings?pii_type=email"
curl "http://127.0.0.1:8000/scans/<SCAN_ID>/findings"
```

Findings are sorted by risk severity descending, then confidence descending.

## Privacy Notes

The backend stores scanner metadata and masked examples only. It does not call external APIs, does not send telemetry, and does not log raw scanner payload values.

