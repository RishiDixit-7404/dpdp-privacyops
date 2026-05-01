#!/bin/sh
set -eu

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:3000}"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

pass() {
  printf 'PASS %s\n' "$1"
}

fail() {
  printf 'FAIL %s\n' "$1" >&2
  exit 1
}

fetch() {
  url="$1"
  output="$2"
  if curl -fsS "$url" > "$output"; then
    return 0
  fi
  return 1
}

expect() {
  pattern="$1"
  file="$2"
  label="$3"
  if grep -q "$pattern" "$file"; then
    pass "$label"
  else
    fail "$label"
  fi
}

health="$TMP_DIR/health.json"
if fetch "$API_BASE_URL/health" "$health"; then
  expect '"status":"ok"' "$health" "backend health"
else
  fail "backend health unreachable at $API_BASE_URL/health"
fi

docs="$TMP_DIR/docs.html"
if fetch "$API_BASE_URL/docs" "$docs"; then
  expect 'Swagger UI' "$docs" "backend docs"
else
  fail "backend docs unreachable at $API_BASE_URL/docs"
fi

frontend="$TMP_DIR/frontend.html"
if fetch "$FRONTEND_URL" "$frontend"; then
  pass "frontend reachable"
else
  fail "frontend unreachable at $FRONTEND_URL"
fi

API_BASE_URL="$API_BASE_URL" sh scripts/smoke_demo.sh
pass "smoke demo"

printf '%s\n' "READY capture screenshots in this order: dashboard, findings, DSR, consent, evidence, readiness scans"
printf '%s\n' "READY also capture backend docs and terminal PASS output if needed"
