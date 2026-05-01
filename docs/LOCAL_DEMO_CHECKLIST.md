# Local Demo Checklist

## 1. Prerequisites

- Python 3.11+
- Node 18+
- A terminal at the repo root

## 2. Backend Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cd backend
python -m pip install -e ".[dev]"
```

## 3. Migrate

```bash
python -m alembic upgrade head
```

## 4. Seed Demo Data

```bash
cd ..
python scripts/seed_demo.py
```

## 5. Run Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

## 6. Run Frontend

```bash
cd ../frontend
npm install
npm run dev
```

## 7. Smoke Test

```bash
cd ..
bash scripts/smoke_demo.sh
```

## 8. Open URLs

- Backend docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

## 9. Demo Click Path

- Readiness scans: show the Rs. 9,999 package and checklist progress
- Project dashboard: open `Learno AI Tutor`
- Scan findings: review high and critical masked findings
- DSR inbox: open User Data Requests
- Consent events: open Consent Events
- Evidence report: open Evidence Report

## 10. Talk Track

- "We start with a Rs. 9,999 technical readiness scan."
- "We do not want your raw personal data."
- "We do not need production data."
- "The scanner runs inside the customer environment."
- "We store metadata, masked examples, confidence scores, and risk tags."
- "The output is a personal-data inventory, risk map, DSR/consent gap review, and evidence report."
- "The evidence report is technical readiness evidence, not legal certification."
- "If this becomes recurring, the customer moves to monthly monitoring."

## Paid Technical Readiness Scan Workflow

- What it is: a 5-day technical readiness scan for founder-led DPDP discovery.
- Safe inputs: schema dump without data, masked CSV exports, masked logs, privacy notice, third-party tools list, masked AI prompt/log samples.
- Do not ask for raw production data, raw Aadhaar, PAN, phone numbers, emails, student names, secrets, or live identifiers.
- Create a scan at `/readiness-scans`, link it to `Learno AI Tutor`, and track the checklist.
- Run `python scripts/seed_demo.py`, start the backend, then run `bash scripts/smoke_demo.sh`.
- Walk through readiness scan, project dashboard, findings, DSR inbox, consent events, and evidence report.
- This is technical readiness evidence, not legal certification.
