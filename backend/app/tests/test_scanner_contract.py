from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from dpdp_scanner.scanners.json_scanner import scan_json


FIXTURE_PATH = Path(__file__).resolve().parents[3] / "scanner" / "tests" / "fixtures" / "sample_logs.jsonl"
RAW_FIXTURE_VALUES = [
    "rahul.logs@example.com",
    "ananya.logs@example.org",
    "9876543210",
    "ABCDE1234F",
    "1234 5678 9012",
    "rahul@upi",
    "Bearer abcdefghijk123",
    "sk_test_LOGSKEY123456",
    "919876543211",
    "priya.response@example.net",
]


def test_scanner_generated_payload_uploads_and_does_not_leak_raw_pii(
    client: TestClient,
    db_session: Session,
    project_id: str,
) -> None:
    scanner_result = scan_json(FIXTURE_PATH)
    scanner_payload = scanner_result.model_dump(mode="json")
    scanner_finding_ids = {finding["finding_id"] for finding in scanner_payload["findings"]}

    upload_response = client.post(f"/projects/{project_id}/scans/upload", json=scanner_payload)

    assert upload_response.status_code == 201
    upload_payload = upload_response.json()
    assert upload_payload["scanner_scan_id"] == scanner_payload["scan_id"]
    assert upload_payload["raw_pii_uploaded"] is False
    assert upload_payload["summary"]["total_findings"] == len(scanner_payload["findings"])

    scan = db_session.scalar(
        select(models.Scan).where(models.Scan.scanner_scan_id == scanner_payload["scan_id"])
    )
    assert scan is not None
    assert scan.raw_pii_uploaded is False

    findings = list(db_session.scalars(select(models.Finding).where(models.Finding.scan_id == scan.id)).all())
    assert len(findings) == len(scanner_payload["findings"])
    assert {finding.scanner_finding_id for finding in findings} == scanner_finding_ids

    findings_response = client.get(f"/scans/{upload_payload['id']}/findings")
    assert findings_response.status_code == 200
    assert {finding["scanner_finding_id"] for finding in findings_response.json()["items"]} == scanner_finding_ids

    serialized_api_response = json.dumps([upload_payload, findings_response.json()])
    serialized_stored_examples = json.dumps([finding.masked_examples for finding in findings])
    for raw_value in RAW_FIXTURE_VALUES:
        assert raw_value not in serialized_api_response
        assert raw_value not in serialized_stored_examples
