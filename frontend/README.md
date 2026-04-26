# DPDP PrivacyOps Frontend

Next.js dashboard v0 for the DPDP PrivacyOps data map.

The dashboard lets a local user create projects, upload scanner JSON output, view scans, inspect findings, and filter the personal-data inventory by risk, PII type, source type, and scan.

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
- No telemetry or analytics are included.

