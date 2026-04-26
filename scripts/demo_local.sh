#!/bin/sh
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DATABASE_URL_VALUE="postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp"
if [ -n "${PYTHON:-}" ]; then
  PYTHON_BIN=$PYTHON
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
else
  printf '%s\n' "[demo-local] FAILED: python or python3 is required." >&2
  exit 1
fi

log() {
  printf '%s\n' "[demo-local] $*"
}

cd "$REPO_ROOT"

if ! command -v docker >/dev/null 2>&1; then
  printf '%s\n' "[demo-local] FAILED: docker is required to start the local Postgres compose service." >&2
  exit 1
fi

log "Starting local Postgres service."
docker compose up -d postgres

log "Waiting for Postgres readiness."
attempt=1
while [ "$attempt" -le 60 ]; do
  if docker compose exec -T postgres pg_isready -U dpdp -d dpdp >/dev/null 2>&1; then
    log "Postgres is ready."
    break
  fi
  if [ "$attempt" -eq 60 ]; then
    printf '%s\n' "[demo-local] FAILED: Postgres did not become ready within 60 seconds." >&2
    exit 1
  fi
  attempt=$((attempt + 1))
  sleep 1
done

log "Running backend migrations."
cd "$REPO_ROOT/backend"
DATABASE_URL="$DATABASE_URL_VALUE" "$PYTHON_BIN" -m alembic upgrade head

log "Seeding demo data."
cd "$REPO_ROOT"
DATABASE_URL="$DATABASE_URL_VALUE" "$PYTHON_BIN" scripts/seed_demo_data.py

log "Demo database is ready."
printf '\nStart the backend in one terminal:\n'
printf '  cd backend && DATABASE_URL=%s python -m uvicorn app.main:app --reload\n' "$DATABASE_URL_VALUE"
printf '\nStart the frontend in another terminal:\n'
printf '  cd frontend && NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev\n'
printf '\nOpen:\n'
printf '  http://localhost:3000/projects\n'
