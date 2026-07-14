# DPDP PrivacyOps

Developer-first DPDP PrivacyOps tooling for SaaS, edtech, healthtech, and AI teams.

## Overview

DPDP PrivacyOps provides a set of tools to help teams scan, identify, and manage personally identifiable information (PII) across their systems to comply with the Digital Personal Data Protection (DPDP) Act. 

The repository includes:
- **Scanner**: Local CSV, Postgres metadata, JSON, and JSONL PII discovery scanner.
- **Backend**: FastAPI server for accepting scanner JSON uploads, storing scans/findings, and serving dashboard data.
- **Frontend Dashboard**: Next.js local dashboard for projects, scanner uploads, scans, findings, and filters.
- **DSR Inbox**: User Data Request tracking for access, correction, deletion, consent withdrawal, and grievance workflows.
- **Consent Event API**: Append-only consent event ledger, dashboard view, and Node SDK wrapper.
- **Evidence Report**: Technical readiness evidence summary generated from scanner metadata, DSR records, and consent events.

> [!NOTE]
> This repository does not include auth, billing, evidence report PDF generation, external integrations, automatic deletion across systems, cookie banners, legal notice generation, email notifications, or deployment complexity yet.

## Privacy Guarantee

The scanner inspects local files or Postgres metadata, masks examples before writing output, and emits structured JSON findings only. No external APIs, telemetry, or network uploads are used by the scanner. 

The output contract sets `raw_pii_uploaded` to `false`. Pydantic validation rejects any scanner result that tries to set it to `true`. Evidence reports serve as technical readiness evidence for product and engineering teams.

## Quickstart

### 1. Backend Setup

Use Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cd backend
python -m pip install -e ".[dev]"
```

Database setup and migration:

```bash
cd backend
python -m alembic upgrade head
```

Run backend:

```bash
cd backend
python -m uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
The dashboard will be available at `http://localhost:3000`.

### 3. Demo Data (Optional)

You can seed the local database with demo data:

```bash
python scripts/seed_demo.py
```
This script creates a dummy project with masked scanner examples, DSR workflow records, consent events, and an evidence report. 

You can also run smoke tests to verify the setup:

```bash
bash scripts/smoke_demo.sh
```

## Running the Scanners

### CSV Scan
```bash
dpdp-scanner scan-csv \
  --path scanner/tests/fixtures/sample_customers.csv \
  --output /tmp/findings.json
```

### JSON/JSONL Scan
```bash
dpdp-scanner scan-json \
  --path scanner/tests/fixtures/sample_logs.jsonl \
  --output /tmp/findings_logs.json
```
The JSON scanner treats `message`, `notes`, `payload`, `prompt`, `response`, `metadata`, `ticket_body`, `input_text`, `output_text`, `request_body`, and `response_body` as possible free-text PII locations.

### Postgres Metadata Scan
The scanner reads schema, table, column, and type metadata from `information_schema.columns` only. It does not sample table values.
```bash
dpdp-scanner scan-postgres \
  --database-url "$DATABASE_URL" \
  --metadata-only \
  --output /tmp/postgres-findings.json
```

## SDK Integration

The TypeScript SDK is located in `sdk/node/`.

```ts
import { DpdpPrivacyOpsClient } from "@dpdp-privacyops/node";

const client = new DpdpPrivacyOpsClient({
  apiBaseUrl: "http://localhost:8000",
  projectId: "project-uuid"
});

await client.trackConsent({
  externalUserId: "user_12345",
  purpose: "marketing_whatsapp",
  noticeVersion: "v2.1",
  source: "web_signup"
});
```

## Development and Testing

Backend tests:
```bash
cd backend
pytest
```

Scanner tests:
```bash
pytest --cov=dpdp_scanner
```

Frontend checks:
```bash
cd frontend
npm run typecheck
npm test
```

## Docker

Build the scanner image:
```bash
docker build -f docker/scanner.Dockerfile -t dpdp-scanner .
```

Run a scan via Docker:
```bash
docker run --rm \
  -v "$PWD/scanner/tests/fixtures:/data:ro" \
  -v /tmp:/out \
  dpdp-scanner scan-csv --path /data/sample_customers.csv --output /out/findings.json
```
