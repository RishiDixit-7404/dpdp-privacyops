# DPDP PrivacyOps Frontend

Next.js dashboard v0 for the DPDP PrivacyOps data map.

The dashboard lets a local user create projects, upload scanner JSON output, view scans, inspect findings, filter the personal-data inventory, track User Data Requests, and review consent events.

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

## Commands

```bash
npm run typecheck
npm run build
npm test
npm run lint
```

## Privacy Notes

- Uploaded scanner JSON is parsed client-side only for upload.
- The dashboard does not display raw uploaded JSON.
- The dashboard does not write uploaded scanner JSON to `localStorage` or `sessionStorage`.
- The dashboard does not print uploaded file contents to the console.
- The UI displays only backend-returned metadata and masked examples.
- Privacy request payloads are sent only to the configured backend API and are not stored in browser storage.
- Consent event payloads are sent only to the configured backend API and are not stored in browser storage.
- No telemetry or analytics are included.
