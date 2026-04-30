from __future__ import annotations

from fastapi.testclient import TestClient


def _scan_payload() -> dict[str, object]:
    return {
        "scan_id": "demo-evidence-scan",
        "scanner_version": "0.1.0",
        "scan_type": "json",
        "source": "demo-safe-metadata.json",
        "generated_at": "2026-04-30T10:00:00Z",
        "raw_pii_uploaded": False,
        "findings": [
            {
                "finding_id": "demo_activity_logs_payload",
                "source_type": "json",
                "source_name": "activity-logs-jsonl",
                "table_or_file": "activity_logs",
                "field_name": "payload",
                "pii_type": "free_text_possible_pii",
                "confidence_score": 0.93,
                "risk_level": "critical",
                "detection_method": "combined",
                "masked_examples": ["r***@example.com"],
                "sample_count": 20,
                "match_count": 8,
                "suggested_action": "Add redaction before log ingestion.",
            },
            {
                "finding_id": "demo_users_phone",
                "source_type": "postgres",
                "source_name": "learno-postgres",
                "table_or_file": "users",
                "field_name": "phone",
                "pii_type": "contact_data",
                "confidence_score": 0.97,
                "risk_level": "high",
                "detection_method": "combined",
                "masked_examples": ["98******10"],
                "sample_count": 50,
                "match_count": 45,
                "suggested_action": "Classify as contact data and confirm retention controls.",
            },
        ],
    }


def test_evidence_report_summarizes_demo_readiness(client: TestClient, project_id: str) -> None:
    upload = client.post(f"/projects/{project_id}/scans/upload", json=_scan_payload())
    assert upload.status_code == 201
    data_request = client.post(
        f"/projects/{project_id}/data-requests",
        json={
            "request_type": "access",
            "requester_name": None,
            "requester_email": "r***@example.com",
            "requester_identifier": "student_****",
            "request_details": "Demo request without raw personal data.",
        },
    )
    assert data_request.status_code == 201
    consent = client.post(
        f"/projects/{project_id}/consent-events",
        json={
            "external_user_id": "student_****",
            "purpose": "marketing_whatsapp",
            "status": "granted",
            "notice_version": "demo-v1",
            "source": "demo_seed",
            "occurred_at": "2026-04-30T10:15:00Z",
            "metadata": {"seed": "local_mvp_demo"},
        },
    )
    assert consent.status_code == 201

    response = client.get(f"/projects/{project_id}/evidence-report")

    assert response.status_code == 200
    body = response.json()
    assert body["trust_positioning"] == (
        "We do not want your raw personal data. The scanner runs inside your environment and sends only metadata, "
        "masked examples, confidence scores, and risk tags."
    )
    assert body["systems_scanned"]
    assert body["data_categories"]
    assert body["top_risks"][0]["field_name"] == "payload"
    assert body["dsr_readiness"]["status"] == "demo_ready"
    assert body["consent_readiness"]["status"] == "demo_ready"
    assert "not legal certification" in body["legal_certification_disclaimer"]
    assert "technical readiness evidence" in body["evidence_scope"].lower()
    assert "98******10" in response.text


def test_evidence_report_missing_project_returns_404(client: TestClient) -> None:
    response = client.get("/projects/22222222-2222-4222-8222-222222222222/evidence-report")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
