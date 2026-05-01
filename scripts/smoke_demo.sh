#!/bin/sh
set -eu

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
PROJECT_ID="${DEMO_PROJECT_ID:-22222222-2222-4222-8222-222222222222}"
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
  attempts=0
  while [ "$attempts" -lt 5 ]; do
    if curl -fsS "$url" > "$output"; then
      return 0
    fi
    attempts=$((attempts + 1))
    sleep 1
  done
  fail "request failed: $url"
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
fetch "$API_BASE_URL/health" "$health"
expect '"status":"ok"' "$health" "backend health endpoint"

docs="$TMP_DIR/docs.html"
fetch "$API_BASE_URL/docs" "$docs"
expect 'Swagger UI' "$docs" "backend docs endpoint"

projects="$TMP_DIR/projects.json"
fetch "$API_BASE_URL/projects" "$projects"
expect "$PROJECT_ID" "$projects" "demo project exists"
expect 'Learno AI Tutor' "$projects" "demo project name exists"

findings="$TMP_DIR/findings.json"
fetch "$API_BASE_URL/projects/$PROJECT_ID/findings?limit=100" "$findings"
expect 'users' "$findings" "scan findings include users table"
expect 'ai_tutor_prompts' "$findings" "scan findings include AI prompt table"

requests="$TMP_DIR/requests.json"
fetch "$API_BASE_URL/projects/$PROJECT_ID/data-requests?limit=100" "$requests"
expect '"request_type":"access"' "$requests" "DSR access request exists"
expect '"request_type":"deletion"' "$requests" "DSR deletion request exists"
expect '"request_type":"grievance"' "$requests" "DSR grievance request exists"

consent="$TMP_DIR/consent.json"
fetch "$API_BASE_URL/projects/$PROJECT_ID/consent-summary" "$consent"
expect 'marketing_whatsapp' "$consent" "consent marketing purpose exists"
expect 'ai_tutor_personalisation' "$consent" "consent AI tutor purpose exists"
expect 'product_analytics' "$consent" "consent analytics purpose exists"

evidence="$TMP_DIR/evidence.json"
fetch "$API_BASE_URL/projects/$PROJECT_ID/evidence-report" "$evidence"
expect 'Technical readiness evidence' "$evidence" "evidence report technical scope"
expect 'not legal certification' "$evidence" "evidence report disclaimer"
expect 'systems_scanned' "$evidence" "evidence report systems scanned"
expect 'remediation_gaps' "$evidence" "evidence report remediation gaps"

readiness="$TMP_DIR/readiness.json"
fetch "$API_BASE_URL/api/readiness-scans" "$readiness"
expect 'DPDP Technical Readiness Scan' "$readiness" "readiness scan package exists"
expect 'Acme EdTech' "$readiness" "readiness scan customer exists"
expect '"price_inr":9999' "$readiness" "readiness scan price exists"

summary="$TMP_DIR/readiness-summary.json"
fetch "$API_BASE_URL/api/readiness-scans/88888888-8888-4888-8888-888888888888/summary" "$summary"
expect 'Schedule 30-minute walkthrough' "$summary" "readiness scan summary next action"
expect '"checklist_completion_percentage":100' "$summary" "readiness scan checklist complete"
