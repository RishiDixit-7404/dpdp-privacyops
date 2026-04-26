# DPDP PrivacyOps

Developer-first DPDP PrivacyOps tooling for Indian SaaS, edtech, healthtech, HRtech, and AI teams.

Current stage:

- **Stage 1 scanner v0.1**: local CSV, Postgres metadata, JSON, and JSONL PII discovery scanner.
- **Stage 2 backend foundation**: FastAPI API for accepting scanner JSON uploads, storing scans/findings, and serving future dashboard data.
- **Stage 2 dashboard v0**: Next.js local dashboard for projects, scanner uploads, scans, findings, and filters.
- **Stage 3 DSR Inbox v0**: User Data Request tracking for access, correction, deletion, consent withdrawal, and grievance workflows.
- **Stage 4 Consent Event API v0**: append-only consent event ledger, dashboard view, and Node SDK wrapper.
- **Stage 5 Evidence Report v0**: JSON-first technical evidence report for scans, findings, DSR workflow, consent events, remediation, and readiness gaps.
- **MVP demo hardening**: local Postgres verification, deterministic demo seed/reset scripts, privacy smoke checks, and a 3-minute demo script.

This repository does not include auth, billing, server-side PDF generation, external integrations, automatic deletion across systems, cookie banners, legal notice generation, email notifications, or deployment complexity yet.

## Privacy Guarantee

The scanner runs inside your environment and does not upload raw personal data. It inspects local files or Postgres metadata, masks examples before writing output, and emits structured JSON findings only.

No external APIs, telemetry, or network uploads are used by the scanner.

The output contract sets `raw_pii_uploaded` to `false`. Pydantic validation rejects any scanner result that tries to set it to `true`.

## Local MVP Demo

This path starts local Postgres, runs migrations, seeds a realistic demo project, and opens the dashboard against the FastAPI backend.

Prerequisites:

- Python 3.11+
- Node 18+ for the current local build
- Docker
- npm

Before any hosted or customer-facing deployment, upgrade Node to current LTS and upgrade Next.js to a non-vulnerable supported version.

If your shell does not provide `python`, use `python3` in the commands below.

Terminal 1, start Postgres and the backend:

```bash
docker compose up -d postgres

cd backend
python -m pip install -e '.[dev]'
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python -m alembic upgrade head
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python -m uvicorn app.main:app --reload
```

Terminal 2, start the frontend:

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Terminal 3, seed demo data:

```bash
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python scripts/seed_demo_data.py
```

Then open:

- Dashboard projects: `http://localhost:3000/projects`
- Evidence report: `http://localhost:3000/projects/<PROJECT_ID>/evidence-report`
- Public privacy request form: `http://localhost:3000/public/projects/<PROJECT_ID>/privacy-request`
- Consent events: `http://localhost:3000/projects/<PROJECT_ID>/consent`

The seed script prints the exact project URLs after it runs.

Helper scripts:

```bash
# Prepare Postgres, run migrations, seed demo data, and print dev-server commands.
bash scripts/demo_local.sh

# Verify migrations and backend tests against live local Postgres.
bash scripts/verify_postgres_backend.sh

# Remove only the demo organization named "Acme EdTech Demo".
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python scripts/reset_demo_data.py

# Run basic privacy/security source checks.
python scripts/privacy_smoke_check.py
```

The demo scenario creates:

- organization: `Acme EdTech Demo`
- project: `Student Learning Platform`
- scanner findings across JSON logs, support tickets, student data, finance payloads, AI prompts, and auth request bodies
- User Data Requests in `new`, `verifying`, `in_progress`, and `completed` states, including one overdue open request
- consent events for `marketing_whatsapp`, `ai_processing`, and `product_analytics`

Use the 3-minute walkthrough in [docs/demo-script.md](docs/demo-script.md).

## Install Locally

Use Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

For runtime-only installation:

```bash
pip install -e .
```

## Run a CSV Scan

```bash
dpdp-scanner scan-csv \
  --path scanner/tests/fixtures/sample_customers.csv \
  --output /tmp/findings.json
```

The output file contains column-level findings with masked examples.

## Run a JSON or JSONL Scan

Use `scan-json` for exported logs, support tickets, AI prompts, webhook payloads, and other free-text JSON data.

```bash
dpdp-scanner scan-json \
  --path scanner/tests/fixtures/sample_logs.jsonl \
  --output /tmp/findings_logs.json
```

For a `.json` file:

```bash
dpdp-scanner scan-json \
  --path scanner/tests/fixtures/sample_prompts.json \
  --output /tmp/findings_prompts.json
```

Supported inputs:

- `.json`: a single object, an array of objects, nested objects, and nested arrays
- `.jsonl`: one JSON object per line

Nested fields are flattened into stable logical paths. For example, `{"user": {"email": "..."}}` becomes `user.email`, and arrays use `[]` instead of numeric indexes, such as `messages[].text` or `events[].payload.input_text`. Numeric indexes are excluded so downstream `finding_id` values remain stable across repeated scans.

The JSON scanner is designed for the log/prompt/support-ticket privacy use case: fields such as `message`, `notes`, `payload`, `prompt`, `response`, `metadata`, `ticket_body`, `input_text`, `output_text`, `request_body`, and `response_body` are treated as possible free-text PII locations. Regex PII found inside these fields is reported with masked examples and redaction-focused suggested actions.

## Run a Postgres Metadata Scan

Scanner v0 reads schema, table, column, and type metadata from `information_schema.columns` only. It does not sample table values.

```bash
dpdp-scanner scan-postgres \
  --database-url "$DATABASE_URL" \
  --metadata-only \
  --output /tmp/postgres-findings.json
```

## Run Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=dpdp_scanner
```

## Backend Foundation

The backend lives in `backend/` and provides:

- `GET /health`
- project creation/list/detail APIs
- scanner JSON upload API at `POST /projects/{project_id}/scans/upload`
- scan list/detail APIs
- findings APIs with filters for risk level, PII type, source type, and scan ID
- paginated findings responses for dashboard tables
- DSR Inbox APIs for User Data Requests, notes, and audit events
- Consent Event APIs for append-only granted/withdrawn events, current status lookup, and event-count summaries
- Evidence Report API for DPDP readiness evidence across scans, risk inventory, DSR workflow, consent events, remediation, and gaps

The scanner-to-backend flow is:

1. Run the local scanner inside the customer environment.
2. Scanner writes JSON with masked examples only and `raw_pii_uploaded: false`.
3. Upload that JSON to the backend project scan endpoint.
4. Backend validates the scanner output contract and stores scans/findings in Postgres.

Backend setup:

```bash
cd backend
python -m pip install -e ".[dev]"
alembic upgrade head
python -m uvicorn app.main:app --reload
```

Backend tests:

```bash
cd backend
pytest
```

Backend tests use SQLite in-memory by default. To run them against local Postgres:

```bash
docker compose up -d postgres
cd backend
BACKEND_TEST_DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp_test pytest
```

Or run the full live Postgres backend verification path from the repo root:

```bash
bash scripts/verify_postgres_backend.sh
```

Local Postgres is available with:

```bash
docker compose up -d postgres
```

Run the backend migration against local Postgres with:

```bash
cd backend
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python -m alembic upgrade head
```

## Frontend Dashboard

The Next.js dashboard lives in `frontend/`.

```bash
cd frontend
npm install
npm run dev
```

Set the API base URL with:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Dashboard checks:

```bash
cd frontend
npm run typecheck
npm run build
npm test
```

The dashboard workflow is:

1. Run the FastAPI backend.
2. Run the scanner and produce a JSON findings file.
3. Create a project in the dashboard.
4. Upload scanner JSON from the project page.
5. Review scans, risk summaries, and filtered findings.
6. Open User Data Requests to track privacy requests, notes, and audit events.
7. Open Consent Events to record and verify purpose-based consent events.
8. Open Evidence Report to review a technical DPDP readiness evidence summary.

DSR Inbox routes:

- Admin inbox: `/projects/<PROJECT_ID>/requests`
- Request detail: `/projects/<PROJECT_ID>/requests/<REQUEST_ID>`
- Public intake form: `/public/projects/<PROJECT_ID>/privacy-request`

Request types are `access`, `correction`, `deletion`, `consent_withdrawal`, and `grievance`. Statuses are `new`, `verifying`, `in_progress`, `completed`, and `rejected`.

DSR Inbox v0 is workflow tracking only. It does not implement auth, automatic deletion, email notifications, identity verification automation, or evidence report PDF generation.

## Consent Event API

Consent Event API v0 is an append-only developer API. Customers record consent events with `external_user_id`, `purpose`, `status`, `notice_version`, optional `source`, `occurred_at`, and optional metadata.

Backend endpoints:

- `POST /projects/{project_id}/consent-events`
- `GET /projects/{project_id}/consent-events`
- `GET /projects/{project_id}/consent-status`
- `GET /projects/{project_id}/consent-summary`

Dashboard route:

- `/projects/<PROJECT_ID>/consent`

Privacy rule: consent events use `external_user_id` only. They do not require email, phone, or name.

Consent summary counts are event counts in v0, not unique-user counts.

## Node SDK

The TypeScript SDK lives in `sdk/node/`.

```bash
cd sdk/node
npm install --no-audit --no-fund
npm run typecheck
npm test
npm run build
```

Basic usage:

```ts
import { DpdpPrivacyOpsClient } from "@dpdp-privacyops/node";

const client = new DpdpPrivacyOpsClient({
  apiBaseUrl: "http://localhost:8000",
  projectId: "project-uuid"
});

await client.trackConsent({
  externalUserId: "usr_123",
  purpose: "marketing_whatsapp",
  noticeVersion: "v2.1",
  source: "web_signup"
});
```

API key enforcement is not implemented yet; the SDK accepts `apiKey` for future compatibility.

## Evidence Report v0

Evidence Report v0 is a JSON-first technical evidence report. It aggregates existing project data and does not persist generated reports in v0.

Backend endpoint:

- `GET /projects/{project_id}/evidence-report`

Dashboard route:

- `/projects/<PROJECT_ID>/evidence-report`

Report sections:

- Executive Summary
- Scan & Data Inventory
- Risk Summary
- Top Risks
- User Data Request Workflow
- Consent Event Ledger
- Recommended Remediation
- Readiness Gaps

The dashboard includes a browser print button, so users can use the browser print-to-PDF workflow. There is no server-side PDF designer or PDF generation in v0.

Disclaimer: Evidence Report v0 is a technical evidence report for DPDP readiness evidence. It is not a legal compliance certificate.

## Output Schema

Top-level JSON fields:

- `scan_id`: UUID string generated per scan
- `scanner_version`: scanner package version
- `scan_type`: `csv`, `postgres`, or `json`
- `source`: scanned filename or sanitized Postgres source
- `generated_at`: UTC timezone-aware ISO timestamp
- `raw_pii_uploaded`: always `false`
- `findings`: list of column-level findings

Each finding includes:

- `finding_id`: deterministic ID derived from source type, source name, table/file, field name, and PII type
- `source_type`, `source_name`, `table_or_file`, `field_name`
- `pii_type`
- `confidence_score`
- `risk_level`
- `detection_method`
- `masked_examples`: masked values only, capped at three
- `sample_count`, `match_count`
- `suggested_action`

Example shape:

```json
{
  "scan_id": "f3e4aaf4-6e0d-4a42-96a8-5a686bcf0f2b",
  "scanner_version": "0.1.0",
  "scan_type": "csv",
  "source": "sample_customers.csv",
  "generated_at": "2026-04-26T12:00:00Z",
  "raw_pii_uploaded": false,
  "findings": [
    {
      "finding_id": "fnd_2a37f9dd0e50a9dfd81a112e",
      "source_type": "csv",
      "source_name": "sample_customers.csv",
      "table_or_file": "sample_customers.csv",
      "field_name": "email",
      "pii_type": "email",
      "confidence_score": 0.95,
      "risk_level": "high",
      "detection_method": "combined",
      "masked_examples": ["r***********@example.com"],
      "sample_count": 100,
      "match_count": 95,
      "suggested_action": "Classify this field as contact data. Ensure purpose limitation, access controls, retention rules, and deletion workflow coverage."
    }
  ]
}
```

## Inspect Output Safely

The JSON should contain masked examples and metadata only. To inspect without dumping every field:

```bash
jq '{scan_id, scan_type, source, generated_at, raw_pii_uploaded, finding_count: (.findings | length)}' /tmp/findings.json
jq '.findings[] | {finding_id, field_name, pii_type, risk_level, detection_method, masked_examples}' /tmp/findings.json
```

## Docker

Build from the repository root:

```bash
docker build -f docker/scanner.Dockerfile -t dpdp-scanner .
```

Run a CSV scan by mounting a local directory:

```bash
docker run --rm \
  -v "$PWD/scanner/tests/fixtures:/data:ro" \
  -v /tmp:/out \
  dpdp-scanner scan-csv --path /data/sample_customers.csv --output /out/findings.json
```

## Known Limitations

- no auth
- no billing
- no hosted deployment
- no server-side PDF generation
- no automatic deletion across systems
- no email notifications
- no external integrations
- no API key enforcement for the consent SDK yet
- Next.js is pinned for the current local Node 18 path and must be upgraded before production or any customer-facing deployment

## Production Hardening Checklist

- Upgrade Node to current LTS.
- Upgrade Next.js to a non-vulnerable supported version.
- Add auth, project-level access control, and API key enforcement.
- Add hosted deployment configuration and secret management.
- Add production database backups, retention controls, and operational monitoring.
- Add server-side report persistence or export only after the JSON-first workflow is validated.
