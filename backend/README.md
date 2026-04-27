# DPDP PrivacyOps Backend

FastAPI backend foundation for DPDP PrivacyOps. This service accepts local scanner JSON output, validates the privacy contract, stores scans and findings, and exposes APIs for the dashboard. It also includes DSR Inbox v0, Consent Event API v0 with API-key-protected writes, and Evidence Report v0.

It does not include full user login/auth, billing, server-side PDF generation, automatic deletion across systems, cookie banners, email notifications, external integrations, or frontend code.

Full user auth is intentionally not implemented yet. Consent event writes require project API keys, but the remaining APIs are the local/backend foundation for the dashboard and should not be exposed publicly without a full auth layer.

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

From the repo root, the full live Postgres verification path is:

```bash
bash scripts/verify_postgres_backend.sh
```

That script starts the existing compose `postgres` service, waits for readiness, runs Alembic against `dpdp`, and runs backend tests against `dpdp_test`.

## Demo Seed Data

From the repo root, seed a local demo project after migrations:

```bash
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python scripts/seed_demo_data.py
```

The seed creates or reuses:

- organization: `Acme EdTech Demo`
- project: `Student Learning Platform`
- masked scanner findings across logs, support tickets, student data, finance payloads, AI prompts, and auth request bodies
- User Data Requests with notes and audit events
- consent events for multiple purposes

Reset only that demo organization and its related data:

```bash
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python scripts/reset_demo_data.py
```

The reset script has a hard guard: it deletes only organizations named `Acme EdTech Demo`.

## Endpoint List

- `GET /health`
- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `POST /projects/{project_id}/api-keys`
- `GET /projects/{project_id}/api-keys`
- `POST /projects/{project_id}/api-keys/{api_key_id}/revoke`
- `POST /projects/{project_id}/scans/upload`
- `GET /projects/{project_id}/scans`
- `GET /scans/{scan_id}`
- `GET /projects/{project_id}/findings`
- `GET /scans/{scan_id}/findings`
- `POST /projects/{project_id}/data-requests`
- `GET /projects/{project_id}/data-requests`
- `GET /data-requests/{request_id}`
- `PATCH /data-requests/{request_id}`
- `POST /data-requests/{request_id}/notes`
- `POST /public/projects/{project_id}/data-requests`
- `POST /projects/{project_id}/consent-events`
- `GET /projects/{project_id}/consent-events`
- `GET /projects/{project_id}/consent-status`
- `GET /projects/{project_id}/consent-summary`
- `GET /projects/{project_id}/evidence-report`

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

## DSR Inbox APIs

DSR Inbox v0 uses clearer product wording in the UI: User Data Request or Privacy Request. It tracks request workflow and evidence only. Auth, identity verification automation, email notifications, and automatic deletion across systems are intentionally not implemented yet.

Request types:

- `access`
- `correction`
- `deletion`
- `consent_withdrawal`
- `grievance`

Statuses:

- `new`
- `verifying`
- `in_progress`
- `completed`
- `rejected`

Create an admin-side request:

```bash
curl -X POST http://127.0.0.1:8000/projects/<PROJECT_ID>/data-requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "access",
    "requester_name": "Rahul Sharma",
    "requester_email": "rahul@example.com",
    "requester_identifier": "usr_123",
    "request_details": "Please send me a copy of my data."
  }'
```

List requests with filters and pagination:

```bash
curl "http://127.0.0.1:8000/projects/<PROJECT_ID>/data-requests?status=new&request_type=access&limit=50&offset=0"
```

Update workflow fields:

```bash
curl -X PATCH http://127.0.0.1:8000/data-requests/<REQUEST_ID> \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "assigned_to": "ops-owner",
    "due_date": "2026-05-10T10:00:00Z"
  }'
```

Add a note:

```bash
curl -X POST http://127.0.0.1:8000/data-requests/<REQUEST_ID>/notes \
  -H "Content-Type: application/json" \
  -d '{
    "note": "Verified requester email manually.",
    "created_by": "admin"
  }'
```

Public intake endpoint for a future privacy request form:

```bash
curl -X POST http://127.0.0.1:8000/public/projects/<PROJECT_ID>/data-requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "deletion",
    "requester_email": "rahul@example.com",
    "request_details": "Please delete my account data."
  }'
```

The public endpoint only creates a request and returns a minimal confirmation. It does not expose project data or request lists.

## Consent Event APIs

Consent Event API v0 is an append-only ledger. There are no update or delete APIs for consent events.

Consent event writes require a project API key. API keys are stored hashed and the raw key is returned only once at creation time.

Create an API key:

```bash
curl -X POST http://127.0.0.1:8000/projects/<PROJECT_ID>/api-keys \
  -H "Content-Type: application/json" \
  -d '{"name":"Production consent writer"}'
```

Use the returned key with `Authorization: Bearer <API_KEY>` or `X-DPDP-API-Key: <API_KEY>` when creating consent events. Revoked keys cannot write events. Read endpoints remain unauthenticated in the local MVP.

Consent event statuses:

- `granted`
- `withdrawn`

Record a consent event:

```bash
curl -X POST http://127.0.0.1:8000/projects/<PROJECT_ID>/consent-events \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "usr_123",
    "purpose": "marketing_whatsapp",
    "status": "granted",
    "notice_version": "v2.1",
    "source": "web_signup",
    "occurred_at": "2026-04-26T10:30:00+05:30",
    "metadata": {
      "ip_country": "IN",
      "ui_surface": "signup_checkbox"
    }
  }'
```

List events:

```bash
curl "http://127.0.0.1:8000/projects/<PROJECT_ID>/consent-events?external_user_id=usr_123&purpose=marketing_whatsapp&status=granted&limit=100&offset=0"
```

Check current consent status:

```bash
curl "http://127.0.0.1:8000/projects/<PROJECT_ID>/consent-status?external_user_id=usr_123&purpose=marketing_whatsapp"
```

Get admin summary:

```bash
curl "http://127.0.0.1:8000/projects/<PROJECT_ID>/consent-summary"
```

Consent summary counts are event counts in v0, not unique-user counts.

Privacy rule: consent events use `external_user_id` only. The API does not ask for email, phone, or name. Optional metadata is capped at 10KB.

Full user login/auth is intentionally not implemented yet. API key enforcement currently protects consent event writes only.

## Evidence Report API

Evidence Report v0 is JSON-first and generated on demand. Reports are not persisted in v0.

Endpoint:

```bash
curl "http://127.0.0.1:8000/projects/<PROJECT_ID>/evidence-report"
```

The report aggregates:

- project details
- scan count and latest scan
- findings by risk level, PII type, and source type
- top critical/high findings
- sources scanned and scan types
- User Data Request counts, open requests, and overdue requests
- consent event counts and purpose summaries
- deterministic remediation actions
- deterministic readiness gaps

The response includes this disclaimer:

```text
This report is technical evidence of discovered data flows, risks, and workflow status. It is not a legal compliance certificate.
```

Evidence Report v0 is a technical evidence report for DPDP readiness evidence. It is not a legal certificate, and it does not perform legal review.

Demo data seeded by `scripts/seed_demo_data.py` populates this endpoint enough to show scans, findings, DSR workflow status, consent events, remediation actions, and readiness gaps.

## Error Responses

Errors are JSON and avoid echoing submitted scanner values. Expected statuses:

- duplicate scanner scan ID: `409`
- missing project or scan: `404`
- invalid payloads or invalid enum filters: `422`
- missing consent status: `404`
- missing evidence report project: `404`

## Privacy Notes

The backend stores scanner metadata and masked examples only for scanner uploads. Consent events are keyed by `external_user_id` and purpose; no raw email, phone, or name fields are required. It does not call external APIs, does not send telemetry, and does not log raw scanner or request payload values.

Run the repo-level guardrail check from the repo root:

```bash
python scripts/privacy_smoke_check.py
```
