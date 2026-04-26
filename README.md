# DPDP PrivacyOps

Developer-first DPDP PrivacyOps tooling for Indian SaaS, edtech, healthtech, HRtech, and AI teams.

Current stage:

- **Stage 1 scanner v0.1**: local CSV, Postgres metadata, JSON, and JSONL PII discovery scanner.
- **Stage 2 backend foundation**: FastAPI API for accepting scanner JSON uploads, storing scans/findings, and serving future dashboard data.
- **Stage 2 dashboard v0**: Next.js local dashboard for projects, scanner uploads, scans, findings, and filters.

This repository does not include auth, billing, DSR inbox, consent API, evidence report PDF generation, external integrations, or deployment complexity yet.

## Privacy Guarantee

The scanner runs inside your environment and does not upload raw personal data. It inspects local files or Postgres metadata, masks examples before writing output, and emits structured JSON findings only.

No external APIs, telemetry, or network uploads are used by the scanner.

The output contract sets `raw_pii_uploaded` to `false`. Pydantic validation rejects any scanner result that tries to set it to `true`.

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
