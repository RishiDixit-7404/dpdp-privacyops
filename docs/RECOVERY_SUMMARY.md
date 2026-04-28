# DPDP PrivacyOps Recovery Summary

Recovery date: 2026-04-27

## Clone / Pull Status

- Target folder: `c:\Users\Rishi.Dixit\Projects\dpdp-privacyops`
- The folder was empty before recovery.
- Clone succeeded from `https://github.com/RishiDixit-7404/dpdp-privacyops` into the current folder.
- Current branch: `main`
- Remote: `origin https://github.com/RishiDixit-7404/dpdp-privacyops`
- Inspected base commit before this summary: `0fb13a58494623d012d58f97ed7f10105e423e76`
- No existing local repo was present, so no pull was needed.

## Current Folder Structure

- `README.md`: main product, setup, scanner, backend, frontend, SDK, Docker, and limitations documentation.
- `pyproject.toml`: root Python package for the scanner, plus dev dependencies used by backend tests.
- `backend/`: FastAPI backend app, SQLAlchemy models, routers, services, tests, and Alembic migrations.
- `frontend/`: Next.js dashboard app, React components, frontend tests, Tailwind config, and npm lockfile.
- `scanner/`: Python `dpdp_scanner` package with Typer CLI, detectors, CSV/JSON/Postgres scanners, risk scoring, masking, output models, fixtures, and tests.
- `sdk/node/`: TypeScript Node SDK for consent events, with tests and npm lockfile.
- `docker-compose.yml`: local Postgres service.
- `docker/scanner.Dockerfile`: Docker image for the scanner CLI.
- `docker/postgres/init/01-create-test-db.sql`: Postgres init script for test database creation.
- `scripts/`: local demo, seed/reset, privacy smoke check, and live Postgres verification helpers.
- `docs/demo-script.md`: short MVP demo walkthrough.
- `docs/RECOVERY_SUMMARY.md`: this recovery report.

## Detected Stack

- Frontend framework: Next.js `13.5.6` with React `18.2.0`, TypeScript, Tailwind CSS, and Vitest.
- Backend framework: FastAPI with Uvicorn.
- Database: SQLAlchemy-supported database, default SQLite for quick local development, Postgres 16 for local Docker/dev.
- ORM / migrations: SQLAlchemy 2.x ORM and Alembic migrations in `backend/alembic`.
- Auth approach: minimal local-MVP email/password auth now protects dashboard/admin APIs with bearer tokens and organization memberships. Project API keys still protect consent event writes.
- Job queue: none detected.
- Scanner language/runtime: Python 3.11+, Typer CLI, pandas, pydantic, psycopg.
- Report generation: backend generates JSON-first evidence report on demand; frontend renders it and uses browser `window.print()` for print-to-PDF. No server-side PDF generation.
- SDK folder: `sdk/node/`, TypeScript SDK for the Consent Event API. SDK write calls now require `apiKey` and send it as `Authorization: Bearer <apiKey>`.
- Docker/local deployment: `docker-compose.yml` starts Postgres only; `docker/scanner.Dockerfile` builds scanner CLI image. No full app deployment stack detected.

## Package Managers And Dependency Files

- Python package manager style: `pip install -e`, setuptools via `pyproject.toml`.
- Python dependency files:
  - `pyproject.toml`
  - `backend/pyproject.toml`
- Node package manager style: npm.
- Node dependency files:
  - `frontend/package.json`
  - `frontend/package-lock.json`
  - `sdk/node/package.json`
  - `sdk/node/package-lock.json`

## Environment Examples

- `backend/.env.example`
  - `APP_ENV`
  - `DATABASE_URL`
  - `CORS_ORIGINS`
- `frontend/.env.example`
  - `NEXT_PUBLIC_API_BASE_URL`

No real secrets were created or exposed during recovery.

## Database / Migration Setup

- Backend database module: `backend/app/database.py`
- Backend models: `backend/app/models.py`
- Alembic config: `backend/alembic.ini`
- Alembic env: `backend/alembic/env.py`
- Migrations:
  - `backend/alembic/versions/20260426_0001_initial.py`
  - `backend/alembic/versions/20260426_0002_data_requests.py`
  - `backend/alembic/versions/20260426_0003_consent_events.py`

No migrations were run during this recovery pass.

## Tests Detected

- Scanner tests: `scanner/tests/`
- Backend tests: `backend/app/tests/`
- Frontend tests: `frontend/tests/basic.test.tsx`
- SDK tests: `sdk/node/tests/client.test.ts`
- Test tools detected: pytest, Vitest, Testing Library.

Tests were inspected but not executed during this recovery pass, to avoid installing packages or requiring external services.

## Completed Modules

| Product area | Status | Evidence |
| --- | --- | --- |
| PII Discovery Scanner | complete | Python scanner has CLI commands for CSV, JSON/JSONL, and Postgres metadata, masking, output models, risk scoring, fixtures, and tests. |
| Data Map Dashboard | partially complete | Next.js dashboard supports projects, scan uploads, scan list, summaries, findings filters/table, DSR, consent, and evidence report views. It is still a local MVP dashboard, not a full production data map. |
| DSR Inbox | partially complete | Backend CRUD/workflow APIs and frontend inbox/detail/public intake exist. Identity verification automation, auth, email, and automatic deletion are intentionally missing. |
| Consent Event API | partially complete | Append-only backend API, current status, summaries, frontend ledger, Node SDK, and API key enforcement for writes exist. Full preference-center/cookie-banner capabilities are missing. |
| Evidence Report | partially complete | Backend builds report JSON on demand and frontend renders sections with browser print. No persisted report records or server-side PDF generation. |
| Auth / organisations / projects | partially complete | Users, organization memberships, project access checks, login/register, and protected dashboard APIs exist. Enterprise auth, invites, password reset, and role-management UI are missing. |
| Scan upload flow | complete | Backend `POST /projects/{project_id}/scans/upload` validates scanner contract and stores scans/findings; frontend uploads scanner JSON. |
| Findings table | complete | Backend findings APIs support filters/pagination; frontend table shows risk, PII type, source, field, confidence, masked examples, and suggested action. |
| Risk scoring | complete | Scanner risk scoring exists in `scanner/dpdp_scanner/risk.py`, with tests covering scanner behavior. |
| CSV/JSON upload | partially complete | Scanner can scan CSV and JSON/JSONL locally. Frontend uploads generated scanner JSON output only; it does not upload raw CSV/JSON files for server-side scanning. |
| Postgres scanner | partially complete | Scanner supports metadata-only Postgres scanning via `information_schema.columns`. It does not sample table values. |
| PDF/HTML report export | partially complete | Browser print-to-PDF exists. No dedicated HTML export file, server-side PDF generator, or report persistence. |
| Tests | partially complete | Test suites exist for scanner, backend, frontend, and SDK. They were not run in this recovery pass, and production/e2e coverage is not evident. |

## Missing Modules / Known Gaps

- Enterprise auth, OAuth/SAML/SSO, MFA, password reset, invitations, and role-management UI.
- Broader API key coverage beyond consent writes.
- Billing.
- Hosted deployment configuration beyond local Postgres and scanner Docker image.
- Job queue / background worker.
- Server-side PDF generation or persisted report history.
- Automatic deletion across external systems.
- Email notifications.
- External integrations.
- Cookie banner / consent preference center.
- Legal notice generation.
- Production secret management, backups, monitoring, and retention operations.
- Next.js is pinned to `13.5.6`; README warns to upgrade Node and Next.js before production/customer-facing use.

## How To Run Locally

Commands below are taken from repo READMEs unless marked inferred.

### Install Scanner / Root Python Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Windows PowerShell equivalent is inferred:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### Run Scanner

```bash
dpdp-scanner scan-csv --path scanner/tests/fixtures/sample_customers.csv --output /tmp/findings.json
dpdp-scanner scan-json --path scanner/tests/fixtures/sample_logs.jsonl --output /tmp/findings_logs.json
dpdp-scanner scan-postgres --database-url "$DATABASE_URL" --metadata-only --output /tmp/postgres-findings.json
```

PowerShell output paths are inferred:

```powershell
dpdp-scanner scan-csv --path scanner/tests/fixtures/sample_customers.csv --output $env:TEMP\findings.json
dpdp-scanner scan-json --path scanner/tests/fixtures/sample_logs.jsonl --output $env:TEMP\findings_logs.json
```

### Install Backend Dependencies

```bash
cd backend
python -m pip install -e ".[dev]"
```

### Run Backend Locally

SQLite quick local default:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Postgres-backed local path:

```bash
docker compose up -d postgres
cd backend
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python -m alembic upgrade head
DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp python -m uvicorn app.main:app --reload
```

PowerShell env syntax is inferred:

```powershell
$env:DATABASE_URL="postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp"
cd backend
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

### Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Run Frontend Locally

```bash
cd frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

PowerShell env syntax is inferred:

```powershell
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
cd frontend
npm run dev
```

### Install And Run Node SDK Checks

```bash
cd sdk/node
npm install --no-audit --no-fund
npm run typecheck
npm test
npm run build
```

### Run Tests

Root scanner + backend tests:

```bash
pytest
```

Backend tests:

```bash
cd backend
pytest
```

Backend tests against local Postgres:

```bash
docker compose up -d postgres
cd backend
BACKEND_TEST_DATABASE_URL=postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp_test pytest
```

Frontend checks:

```bash
cd frontend
npm run typecheck
npm run build
npm test
npm run lint
```

SDK checks:

```bash
cd sdk/node
npm run typecheck
npm test
npm run build
```

### Docker / Dev Setup

Start local Postgres:

```bash
docker compose up -d postgres
```

Build scanner image:

```bash
docker build -f docker/scanner.Dockerfile -t dpdp-scanner .
```

Run scanner image:

```bash
docker run --rm -v "$PWD/scanner/tests/fixtures:/data:ro" -v /tmp:/out dpdp-scanner scan-csv --path /data/sample_customers.csv --output /out/findings.json
```

Demo helper:

```bash
bash scripts/demo_local.sh
```

## Repo Health Notes

- The repo has coherent README coverage for scanner, backend, frontend, SDK, Docker, known limitations, and demo setup.
- The codebase is split cleanly into frontend, backend, scanner, SDK, scripts, Docker, and docs.
- There are tests across all major areas, though they were not executed during recovery.
- The backend defaults to SQLite for quick local dev, while documented production-like local paths use Postgres.
- The local Docker setup only provisions Postgres; backend/frontend are run directly via Python/npm.
- A few frontend strings display mojibake for separator characters, and some copy uses a non-ASCII dash. These may need a text encoding cleanup later, but no product code was changed in this task.

## Known Blockers

- Auth is local-MVP only. Consent writes require project API keys, dashboard/admin APIs require user bearer tokens, but the app should remain local-only until production auth/session hardening is done.
- Next.js version is old and documented as needing upgrade before hosted/customer-facing deployment.
- Full local verification was not run during this recovery pass because the requested scope was safe inspection and documentation only.
- Any Postgres migration/test verification requires Docker and local database startup.
- Server-side PDF/report export is not present.

## Likely Next Build Step

The next highest-value build step is to harden auth for real team use: invitations, role management UI, password reset, production token/session strategy, and deployment secret handling.

Before that feature work, run the existing verification matrix once on the recovered machine:

```bash
pytest
cd frontend && npm install && npm run typecheck && npm test
cd ../sdk/node && npm install --no-audit --no-fund && npm run typecheck && npm test
python scripts/privacy_smoke_check.py
```

## Recommended Next Codex Prompt

```text
You are working on the DPDP PrivacyOps repo. Read docs/RECOVERY_SUMMARY.md first. Do not refactor broadly.

Goal: harden the local-MVP auth foundation for team usage.

Tasks:
1. Inspect backend models, routers, tests, and frontend API usage.
2. Propose a small invitation and role-management design that fits the existing FastAPI + SQLAlchemy + Alembic stack.
3. Implement only the first safe increment: owner/admin can invite users to an organization and assign member/admin roles, with tests and docs.
4. Do not add billing, hosted deployment, or unrelated UI redesign.
5. Run the relevant tests and report exact commands/results.
```
