# DPDP PrivacyOps Backend

FastAPI backend foundation for Stage 2 of DPDP PrivacyOps. This service accepts local scanner JSON output, validates the privacy contract, stores scans and findings, and exposes APIs for the future dashboard.

It does not include auth, billing, DSR handling, consent APIs, evidence reports, external integrations, or frontend code.

Auth is intentionally not implemented yet. These APIs are the local/backend foundation for the upcoming dashboard and should not be exposed publicly without an auth layer.

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

- `DATABASE_URL`: SQLAlchemy database URL. Local Postgres example: `postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp`
- `APP_ENV`: `development`, `test`, or `production`
- `CORS_ORIGINS`: comma-separated allowed origins. Local defaults are `http://localhost:3000,http://127.0.0.1:3000`.

For quick local development without Postgres, the app defaults to `sqlite:///./dpdp_privacyops_dev.db`.

## Local Postgres

From the repo root:

```bash
docker compose up -d postgres
```

The compose file starts Postgres with:

- user: `dpdp`
- password: `dpdp`
- development database: `dpdp`
- test database: `dpdp_test`

The `dpdp_test` database is created by the init script on first container initialization. If you already have an older local volume, recreate it with `docker compose down -v` before `docker compose up -d postgres`.

## Migrations

From `backend/`:

```bash
alembic upgrade head
```

Against local Postgres:

```bash
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python -m alembic upgrade head
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

Tests use SQLite in-memory by default for reliability. The models and Alembic migration are kept Postgres-compatible for local Postgres and production later.

To run backend tests against Postgres:

```bash
docker compose up -d postgres
cd backend
BACKEND_TEST_DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp_test pytest
```

When `BACKEND_TEST_DATABASE_URL` is set, the test suite creates and drops the app tables in that database. Do not point it at a database with data you need.

## Endpoint List

- `GET /health`
- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `POST /projects/{project_id}/scans/upload`
- `GET /projects/{project_id}/scans`
- `GET /scans/{scan_id}`
- `GET /projects/{project_id}/findings`
- `GET /scans/{scan_id}/findings`

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
curl "http://127.0.0.1:8000/projects/<PROJECT_ID>/findings?source_type=json&limit=50&offset=0"
curl "http://127.0.0.1:8000/scans/<SCAN_ID>/findings"
```

Findings are sorted by risk severity descending, then confidence descending.

Findings responses are paginated:

```json
{
  "items": [],
  "total": 0,
  "limit": 100,
  "offset": 0
}
```

Supported query params:

- `risk_level`: `critical`, `high`, `medium`, or `low`
- `pii_type`: exact PII type string
- `source_type`: `csv`, `postgres`, or `json`
- `scan_id`: scan UUID, on project findings only
- `limit`: default `100`, max `500`
- `offset`: default `0`

## Error Responses

Errors are JSON and avoid echoing submitted scanner values. Expected statuses:

- duplicate scanner scan ID: `409`
- missing project or scan: `404`
- invalid payloads or invalid enum filters: `422`

## Privacy Notes

The backend stores scanner metadata and masked examples only. It does not call external APIs, does not send telemetry, and does not log raw scanner payload values.
