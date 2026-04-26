#!/bin/sh
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DATABASE_URL_VALUE="postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp"
TEST_DATABASE_URL_VALUE="postgresql+psycopg://dpdp:dpdp@localhost:5432/dpdp_test"
if [ -n "${PYTHON:-}" ]; then
  PYTHON_BIN=$PYTHON
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
else
  printf '%s\n' "[verify-postgres] FAILED: python or python3 is required." >&2
  exit 1
fi

log() {
  printf '%s\n' "[verify-postgres] $*"
}

fail() {
  printf '%s\n' "[verify-postgres] FAILED: $*" >&2
  exit 1
}

cd "$REPO_ROOT"

if ! command -v docker >/dev/null 2>&1; then
  fail "docker is required to start the local Postgres compose service."
fi

log "Starting local Postgres service with docker compose."
docker compose up -d postgres

log "Waiting for Postgres readiness."
attempt=1
while [ "$attempt" -le 60 ]; do
  if docker compose exec -T postgres pg_isready -U dpdp -d dpdp >/dev/null 2>&1; then
    log "Postgres is ready."
    break
  fi
  if [ "$attempt" -eq 60 ]; then
    fail "Postgres did not become ready within 60 seconds."
  fi
  attempt=$((attempt + 1))
  sleep 1
done

cd "$REPO_ROOT/backend"

log "Running Alembic migrations against live Postgres."
DATABASE_URL="$DATABASE_URL_VALUE" "$PYTHON_BIN" -m alembic upgrade head

log "Running backend tests against dpdp_test Postgres database."
BACKEND_TEST_DATABASE_URL="$TEST_DATABASE_URL_VALUE" "$PYTHON_BIN" -m pytest

cd "$REPO_ROOT"
log "Live Postgres backend verification passed."
