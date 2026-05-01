# DPDP PrivacyOps

Developer-first DPDP PrivacyOps tooling for Indian SaaS, edtech, healthtech, HRtech, and AI teams.

Current stage:

- **Stage 1 scanner v0.1**: local CSV, Postgres metadata, JSON, and JSONL PII discovery scanner.
- **Stage 2 backend foundation**: FastAPI API for accepting scanner JSON uploads, storing scans/findings, and serving future dashboard data.
- **Stage 2 dashboard v0**: Next.js local dashboard for projects, scanner uploads, scans, findings, and filters.
- **Stage 3 DSR Inbox v0**: User Data Request tracking for access, correction, deletion, consent withdrawal, and grievance workflows.
- **Stage 4 Consent Event API v0**: append-only consent event ledger, dashboard view, and Node SDK wrapper.
- **Stage 5 Evidence Report v0**: technical readiness evidence summary from scanner metadata, DSR records, and consent events.
- **Stage 6 local demo hardening**: deterministic local seed data and smoke checks for the MVP flow.
- **Stage 7 Paid Technical Readiness Scan workflow**: founder-led Rs. 9,999 scan package tracking without payment or billing logic.

This repository does not include auth, billing, evidence report PDF generation, external integrations, automatic deletion across systems, cookie banners, legal notice generation, email notifications, or deployment complexity yet.

## Privacy Guarantee

We do not want your raw personal data. The scanner runs inside your environment and sends only metadata, masked examples, confidence scores, and risk tags.

The scanner inspects local files or Postgres metadata, masks examples before writing output, and emits structured JSON findings only.

No external APIs, telemetry, or network uploads are used by the scanner.

The output contract sets `raw_pii_uploaded` to `false`. Pydantic validation rejects any scanner result that tries to set it to `true`.

Evidence reports are technical readiness evidence for product and engineering teams. They are not legal certification, and raw PII should not be uploaded by default.

## Local MVP Demo

Expected local URLs:

- Backend API: `http://localhost:8000`
- Backend docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

Backend setup:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cd backend
python -m pip install -e ".[dev]"
```

Database setup and migration:

```bash
cd backend
python -m alembic upgrade head
```

Demo seed:

```bash
cd ..
python scripts/seed_demo.py
```

Backend run:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Frontend setup and run:

```bash
cd ../frontend
npm install
npm run dev
```

Smoke test, with the backend running:

```bash
cd ..
bash scripts/smoke_demo.sh
```

The seed creates `Acme EdTech` / `Learno AI Tutor` with masked scanner examples, DSR workflow records, consent events, a readiness scan package, and an evidence report. The seed is safe to run more than once because it resets only its fixed demo rows before recreating them.

## Paid Technical Readiness Scan Workflow

The first paid motion is a Rs. 9,999 one-time DPDP Technical Readiness Scan. It is an operational workflow for founder-led delivery, not billing, payments, or subscription management.

Safe customer inputs to ask for:

- schema dump without data
- masked CSV/sample exports
- log samples with PII masked
- privacy policy or notice link/text
- list of third-party tools
- masked AI prompt/log sample if relevant

Do not ask for raw production data, raw Aadhaar, PAN, phone numbers, emails, student names, secrets, or live identifiers.

In the product, open `/readiness-scans`, create a readiness scan linked to a project, track the safe-input checklist, run/import scanner findings, and open the evidence report. For the local demo, run `python scripts/seed_demo.py`, start the backend, then run `bash scripts/smoke_demo.sh`.

Demo walkthrough:

- "We start with a Rs. 9,999 technical readiness scan."
- "We do not need production data."
- "The scanner runs locally in your environment."
- "The output is a personal-data inventory, risk map, DSR/consent gap review, and evidence report."
- "If this becomes recurring, the customer moves to monthly monitoring."

This is technical readiness evidence, not legal certification.

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
- Evidence Report API for technical readiness evidence
- Readiness Scan APIs for the paid technical scan workflow

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
7. Open Evidence Report to review technical readiness evidence and remediation gaps.
8. Open Readiness Scans to show the Rs. 9,999 paid scan package, checklist progress, and next action.

DSR Inbox routes:

- Admin inbox: `/projects/<PROJECT_ID>/requests`
- Request detail: `/projects/<PROJECT_ID>/requests/<REQUEST_ID>`
- Public intake form: `/public/projects/<PROJECT_ID>/privacy-request`

Request types are `access`, `correction`, `deletion`, `consent_withdrawal`, and `grievance`. Statuses are `new`, `verifying`, `in_progress`, `completed`, and `rejected`.

DSR Inbox v0 is workflow tracking only. It does not implement auth, automatic deletion, email notifications, identity verification automation, or evidence report PDF generation.

## Evidence Report

Evidence Report v0 is available at:

- Backend: `GET /projects/{project_id}/evidence-report`
- Dashboard: `/projects/<PROJECT_ID>/evidence-report`

It summarizes systems scanned, data categories, top risks, DSR readiness, consent readiness, and remediation gaps from existing local metadata. It is technical readiness evidence only and is not legal certification.

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
  externalUserId: "student_****",
  purpose: "marketing_whatsapp",
  noticeVersion: "v2.1",
  source: "web_signup"
});
```

API key enforcement is not implemented yet; the SDK accepts `apiKey` for future compatibility.

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
