# Demo Script

Core narrative:

"Most companies think personal data is only in the users table. The product shows where it actually lives: logs, support tickets, AI prompts, exports, and operational workflows."

## Pre-Demo Setup Commands

Terminal 1:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cd backend
python -m pip install -e ".[dev]"
python -m alembic upgrade head
cd ..
python scripts/seed_demo.py
cd backend
python -m uvicorn app.main:app --reload
```

Terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Optional readiness check:

```bash
bash scripts/demo_check.sh
```

## URLs To Open

- Backend docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Exact Click Path

1. Frontend dashboard/projects
2. Project detail: `Learno AI Tutor`
3. Scan findings
4. DSR inbox
5. Consent events
6. Evidence report
7. Readiness scans

## Screen Talk Track

### Dashboard / Projects

Say: "We start with a technical view of a product, not a legal questionnaire. This demo uses Acme EdTech and the Learno AI Tutor project."

Capture: project list or home/dashboard.

Customer should understand: the workflow starts from a real product/project.

### Project Detail

Say: "The project page brings together scanner output, risk summary, and links into DSR, consent, and evidence workflows."

Capture: project detail with the seeded project visible.

Customer should understand: this is an operational privacy workspace.

### Scan Findings

Say: "Most companies think personal data is only in the users table. The product shows where it actually lives: logs, support tickets, AI prompts, exports, and operational workflows."

Say: "The examples are masked. We do not want raw personal data in the tool."

Capture: findings table showing high/critical risks and masked examples.

Customer should understand: hidden personal-data locations become visible without uploading raw personal data.

### DSR Inbox

Say: "The paid scan also checks whether access, deletion, and grievance requests can be tracked cleanly."

Capture: DSR inbox showing access, deletion, and grievance records.

Customer should understand: readiness includes workflow gaps, not only scanner findings.

### Consent Events

Say: "Consent readiness is about proving granted and withdrawn events for specific purposes."

Capture: consent events or consent summary.

Customer should understand: consent evidence needs an event trail.

### Evidence Report

Say: "This is the output the founder or CTO can use in customer, investor, or internal engineering conversations."

Say: "This is technical readiness evidence, not legal certification."

Capture: systems scanned, data categories, top risks, DSR/consent readiness, and remediation gaps.

Customer should understand: the report is practical evidence and a fix list.

### Readiness Scans

Say: "This is how we run the Rs. 9,999 paid scan manually: safe-input checklist, status, evidence links, and next action."

Say: "We do not want your raw personal data. The scanner runs inside your environment and sends only metadata, masked examples, confidence scores, and risk tags."

Capture: pricing card, checklist progress, and next action.

Customer should understand: the paid scan has a clear package, workflow, and outcome.

## 3-Minute Demo Version

1. Open Readiness Scans and show Rs. 9,999 package.
2. Open Learno AI Tutor project.
3. Show findings across users, support tickets, logs, and AI prompts.
4. Show DSR and consent links briefly.
5. Open Evidence Report and show top risks plus remediation gaps.
6. Close with: "The first step is a 5-day scan. We do not need production data."

## 10-Minute Demo Version

1. Start with the core narrative.
2. Show project dashboard and explain product-scoped review.
3. Spend time on findings and why logs/support/prompts matter.
4. Show DSR inbox and consent event evidence.
5. Show Evidence Report sections one by one.
6. Show Readiness Scans workflow and safe-input checklist.
7. Explain deliverable, 30-minute walkthrough, and monthly monitoring path.
8. Ask: "Which systems would you want checked first: database schema, logs, support tickets, AI prompts, or third-party tools?"
