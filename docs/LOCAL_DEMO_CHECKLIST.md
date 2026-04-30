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

- Project dashboard: open `Learno AI Tutor`
- Scan findings: review high and critical masked findings
- DSR inbox: open User Data Requests
- Consent events: open Consent Events
- Evidence report: open Evidence Report

## 10. Talk Track

- "We do not want your raw personal data."
- "The scanner runs inside the customer environment."
- "We store metadata, masked examples, confidence scores, and risk tags."
- "The evidence report is technical readiness evidence, not legal certification."
