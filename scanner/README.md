# DPDP Scanner

Local scanner v0 for discovering likely personal data in CSV files and Postgres metadata.

## Install

From the repository root:

```bash
pip install -e ".[dev]"
```

## CSV Scan

```bash
dpdp-scanner scan-csv \
  --path scanner/tests/fixtures/sample_customers.csv \
  --output /tmp/findings.json
```

## JSON and JSONL Scan

Use `scan-json` for logs, support tickets, AI prompt exports, webhook payloads, and other JSON/free-text files.

```bash
dpdp-scanner scan-json \
  --path scanner/tests/fixtures/sample_logs.jsonl \
  --output /tmp/findings_logs.json
```

```bash
dpdp-scanner scan-json \
  --path scanner/tests/fixtures/sample_prompts.json \
  --output /tmp/findings_prompts.json
```

Supported inputs:

- `.json` files containing a single object, an array of objects, nested objects, or nested arrays
- `.jsonl` files containing one JSON object per line

Nested JSON paths are flattened into stable field names:

- `user.email`
- `payload.input_text`
- `messages[].text`
- `events[].payload.request_body`

Array indexes are normalized to `[]` and are not included in finding IDs.

## Postgres Metadata Scan

```bash
dpdp-scanner scan-postgres \
  --database-url "$DATABASE_URL" \
  --metadata-only \
  --output /tmp/postgres-findings.json
```

Postgres scanning is metadata-only in v0. It reads from `information_schema.columns` and does not sample table values.

## Output

The scanner writes structured JSON with:

- `scan_id`: UUID string generated per scan
- scanner version
- `scan_type`: `csv`, `postgres`, or `json`
- source name
- UTC timezone-aware generation timestamp
- `raw_pii_uploaded: false`
- column-level findings with deterministic `finding_id` values

Masked examples are capped at three examples per finding.

Finding IDs are deterministic for the same `source_type`, `source_name`, `table_or_file`, `field_name`, and `pii_type`. This lets downstream systems compare repeated scans without depending on row order or timestamps.

Each finding includes:

- `finding_id`
- `source_type`, `source_name`, `table_or_file`, `field_name`
- `pii_type`
- `confidence_score`
- `risk_level`
- `detection_method`
- `masked_examples`
- `sample_count`, `match_count`
- `suggested_action`

## Privacy Guarantee

The scanner runs locally, does not use external APIs, does not send telemetry, and does not upload raw personal data. CSV values are only used locally for detection and masking. Postgres scanning is metadata-only in v0.

`raw_pii_uploaded` is always `false`, and the output schema rejects any other value.

For JSON and JSONL logs, prompts, payloads, and support tickets, free-text fields such as `message`, `notes`, `payload`, `prompt`, `response`, `metadata`, `ticket_body`, `input_text`, `output_text`, `request_body`, and `response_body` are flagged as possible PII locations. PII found inside these fields receives redaction-focused suggested actions.

## Inspect Output Safely

Prefer summaries when reviewing results:

```bash
jq '{scan_id, scan_type, source, generated_at, raw_pii_uploaded, finding_count: (.findings | length)}' /tmp/findings.json
jq '.findings[] | {finding_id, field_name, pii_type, risk_level, masked_examples}' /tmp/findings.json
```

## Tests

```bash
pytest
```

The test suite includes detector tests, masking tests, full-output raw PII leakage tests, schema stability tests, and CLI error behavior tests.
