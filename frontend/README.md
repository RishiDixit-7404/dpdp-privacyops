# DPDP PrivacyOps Frontend

Next.js dashboard v0 for the DPDP PrivacyOps data map.

The dashboard lets a local user create projects, upload scanner JSON output, view scans, inspect findings, filter the personal-data inventory, track User Data Requests, review consent events, and view a technical Evidence Report.

The dashboard has minimal local-MVP auth. Users register or log in with email/password, the frontend stores a bearer token locally, and API calls include `Authorization: Bearer <token>`.

## Setup

Use Node 18+.

Before any hosted or customer-facing deployment, upgrade Node to current LTS and upgrade Next.js to a non-vulnerable supported version.

```bash
cd frontend
npm install
```

Copy `.env.example` if you need to change the API URL:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Run Dev Server

Start the FastAPI backend first:

```bash
cd ../backend
python -m uvicorn app.main:app --reload
```

Then start the dashboard:

```bash
cd ../frontend
npm run dev
```

Open `http://localhost:3000`.

Register at `http://localhost:3000/register` or log in at `http://localhost:3000/login`.

## Local Demo Data

After starting Postgres and running backend migrations, seed the demo project from the repo root:

```bash
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python scripts/seed_demo_data.py
```

The script prints direct URLs for:

- project detail
- User Data Requests
- Consent Events
- Evidence Report
- public Privacy Request intake

Reset only the demo organization and related data:

```bash
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python scripts/reset_demo_data.py
```

## Workflow

1. Run the backend at `http://localhost:8000`.
2. Register or log in.
3. Run the local scanner and write JSON output:

```bash
dpdp-scanner scan-json \
  --path scanner/tests/fixtures/sample_logs.jsonl \
  --output /tmp/findings_logs.json
```

4. Open the dashboard and create a project.
5. Upload `/tmp/findings_logs.json` from the project detail page.
6. Review scans, summaries, findings, filters, and masked examples.
7. Open User Data Requests from the project page to create, filter, update, and evidence privacy requests.
8. Open Consent Events from the project page to create an API key, record granted/withdrawn events, and check current status by user and purpose.
9. Open Evidence Report from the project page to review DPDP readiness evidence and print the report from the browser.

## Auth

Routes:

```text
/register
/login
```

The dashboard protects non-public routes in the app shell. If no token is present, users are sent to `/login`.

The access token is stored in browser `localStorage` for the local MVP. Scanner uploads, privacy request payloads, consent payloads, raw API keys, password hashes, and API key hashes are not stored in browser storage.

## DSR Inbox

Admin dashboard route:

```text
/projects/<PROJECT_ID>/requests
```

Request detail route:

```text
/projects/<PROJECT_ID>/requests/<REQUEST_ID>
```

Public privacy request intake route:

```text
/public/projects/<PROJECT_ID>/privacy-request
```

The inbox supports these request types:

- access
- correction
- deletion
- consent withdrawal
- grievance

The workflow statuses are:

- new
- verifying
- in progress
- completed
- rejected

DSR Inbox v0 is tracking and evidence only. It does not perform automatic deletion, send email notifications, automate identity verification, or add auth.

## Consent Events

Admin dashboard route:

```text
/projects/<PROJECT_ID>/consent
```

The consent page includes:

- project API key list/create/revoke controls
- summary cards
- append-only event creation
- current status checker by `external_user_id` and purpose
- event list with filters for external user ID, purpose, and status

Consent statuses:

- granted
- withdrawn

Consent Event API v0 is an event ledger and developer API. It is not a cookie banner or full preference center. Summary counts are event counts, not unique-user counts in v0.

Privacy rule: the consent form asks for `external_user_id` only. It does not ask for email, phone, or name.

API key rule: create a project API key on the consent page and copy it immediately. The raw key is shown only once and is required to record consent events from the dashboard or SDK.

## Evidence Report

Dashboard route:

```text
/projects/<PROJECT_ID>/evidence-report
```

The Evidence Report page fetches:

```text
GET /projects/{project_id}/evidence-report
```

Report sections:

- Executive Summary
- Scan & Data Inventory
- Risk Summary
- Top Risks
- User Data Request Workflow
- Consent Event Ledger
- Recommended Remediation
- Readiness Gaps

Evidence Report v0 is JSON-first and generated on demand. It is not persisted yet. The dashboard includes a print button that calls the browser print dialog, so users can use browser print-to-PDF. There is no server-side PDF generation in v0.

The report disclaimer is shown clearly:

```text
This report is technical evidence of discovered data flows, risks, and workflow status. It is not a legal compliance certificate.
```

## Commands

```bash
npm run typecheck
npm run build
npm test
npm run lint
```

From the repo root, run the basic privacy/security guardrail:

```bash
python scripts/privacy_smoke_check.py
```

## Privacy Notes

- Uploaded scanner JSON is parsed client-side only for upload.
- The dashboard does not display raw uploaded JSON.
- The dashboard does not write uploaded scanner JSON to `localStorage` or `sessionStorage`.
- The dashboard does not print uploaded file contents to the console.
- The UI displays only backend-returned metadata and masked examples.
- Privacy request payloads are sent only to the configured backend API and are not stored in browser storage.
- Consent event payloads are sent only to the configured backend API and are not stored in browser storage.
- Evidence reports display backend-returned metadata, masked examples, workflow status, and recommended actions.
- No telemetry or analytics are included.

## Known Demo Limitations

- Auth is local-MVP only. There is no OAuth, SAML/SSO, MFA, password reset, invitation flow, or role-management UI yet.
- The dashboard is local-only for the MVP demo.
- Evidence Report v0 uses browser print-to-PDF; there is no server-side PDF generation.
- Automatic deletion across systems and email notifications are not implemented.
- Node and Next.js must be upgraded before production or customer-facing deployment.
