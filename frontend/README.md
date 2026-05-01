# DPDP PrivacyOps Frontend

Next.js dashboard v0 for the DPDP PrivacyOps data map.

The dashboard lets a local user create projects, upload scanner JSON output, view scans, inspect findings, filter the personal-data inventory, track User Data Requests, review consent events, open a technical evidence report, and manage paid readiness scan packages.

Auth is not implemented yet. This is a local MVP dashboard.

## Setup

Use Node 18+.

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

## Workflow

1. Run the backend at `http://localhost:8000`.
2. Run the local scanner and write JSON output:

```bash
dpdp-scanner scan-json \
  --path scanner/tests/fixtures/sample_logs.jsonl \
  --output /tmp/findings_logs.json
```

3. Open the dashboard and create a project.
4. Upload `/tmp/findings_logs.json` from the project detail page.
5. Review scans, summaries, findings, filters, and masked examples.
6. Open User Data Requests from the project page to create, filter, update, and evidence privacy requests.
7. Open Consent Events from the project page to record granted/withdrawn events and check current status by user and purpose.
8. Open Evidence Report from the project page to review systems scanned, data categories, top risks, readiness summaries, and remediation gaps.
9. Open Readiness Scans to show the Rs. 9,999 package, safe-input checklist, summary metrics, and next action.

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

- summary cards
- append-only event creation
- current status checker by `external_user_id` and purpose
- event list with filters for external user ID, purpose, and status

Consent statuses:

- granted
- withdrawn

Consent Event API v0 is an event ledger and developer API. It is not a cookie banner or full preference center. Summary counts are event counts, not unique-user counts in v0.

Privacy rule: the consent form asks for `external_user_id` only. It does not ask for email, phone, or name.

## Evidence Report

Dashboard route:

```text
/projects/<PROJECT_ID>/evidence-report
```

Evidence Report v0 is technical readiness evidence from existing scanner metadata, User Data Request records, and consent events. It is not legal certification.

## Paid Technical Readiness Scan Workflow

Dashboard route:

```text
/readiness-scans
```

Use this page to create and track a Rs. 9,999 one-time DPDP Technical Readiness Scan. Ask for safe inputs only: schema dump without data, masked CSV/sample exports, masked log samples, privacy notice link/text, third-party tools list, and masked AI prompt/log samples if relevant. Do not ask for raw production data or live identifiers.

The page shows checklist progress, high/critical finding count, DSR and consent evidence counts, evidence report links, and the next operational action. This is technical readiness evidence, not legal certification.

## Commands

```bash
npm run typecheck
npm run build
npm test
npm run lint
```

## Privacy Notes

We do not want your raw personal data. The scanner runs inside your environment and sends only metadata, masked examples, confidence scores, and risk tags.

- Uploaded scanner JSON is parsed client-side only for upload.
- The dashboard does not display raw uploaded JSON.
- The dashboard does not write uploaded scanner JSON to `localStorage` or `sessionStorage`.
- The dashboard does not print uploaded file contents to the console.
- The UI displays only backend-returned metadata and masked examples.
- Privacy request payloads are sent only to the configured backend API and are not stored in browser storage.
- Consent event payloads are sent only to the configured backend API and are not stored in browser storage.
- No telemetry or analytics are included.
