from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.tests.conftest import scanner_payload


def upload_scan(client: TestClient, project_id: str, scan_id: str = "report-scan-001") -> dict[str, object]:
    response = client.post(f"/projects/{project_id}/scans/upload", json=scanner_payload(scan_id))
    assert response.status_code == 201
    return response.json()


def create_data_request(
    client: TestClient,
    project_id: str,
    *,
    request_type: str = "access",
    status: str | None = None,
    due_date: str | None = None,
) -> dict[str, object]:
    response = client.post(
        f"/projects/{project_id}/data-requests",
        json={
            "request_type": request_type,
            "requester_name": "Rahul Sharma",
            "requester_email": f"{request_type}@example.com",
            "requester_identifier": f"usr_{request_type}",
            "request_details": "Please process my request.",
            "due_date": due_date,
        },
    )
    assert response.status_code == 201
    body = response.json()
    if status is not None:
        update = client.patch(f"/data-requests/{body['id']}", json={"status": status})
        assert update.status_code == 200
        body = update.json()
    return body


def create_consent_event(
    client: TestClient,
    project_id: str,
    *,
    status: str = "granted",
    purpose: str = "marketing_whatsapp",
) -> dict[str, object]:
    api_key_response = client.post(f"/projects/{project_id}/api-keys", json={"name": "Report test writer"})
    assert api_key_response.status_code == 201
    api_key = api_key_response.json()["api_key"]
    response = client.post(
        f"/projects/{project_id}/consent-events",
        json={
            "external_user_id": "usr_123",
            "purpose": purpose,
            "status": status,
            "notice_version": "v2.1",
            "source": "web_signup",
            "occurred_at": "2026-04-26T10:30:00+05:30",
            "metadata": {"ip_country": "IN"},
        },
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 201
    return response.json()


def get_report(client: TestClient, project_id: str) -> dict[str, object]:
    response = client.get(f"/projects/{project_id}/evidence-report")
    assert response.status_code == 200
    return response.json()


def test_evidence_report_returns_404_for_missing_project(client: TestClient) -> None:
    response = client.get(f"/projects/{uuid4()}/evidence-report")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_empty_project_report_works_with_zero_counts(client: TestClient, project_id: str) -> None:
    report = get_report(client, project_id)

    assert report["report_version"] == "0.1.0"
    assert report["scan_summary"]["scan_count"] == 0
    assert report["risk_summary"]["total_findings"] == 0
    assert report["dsr_summary"]["total_requests"] == 0
    assert report["consent_summary"]["total_events"] == 0
    assert report["top_risks"] == []


def test_report_aggregates_scans_and_findings_correctly(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    report = get_report(client, project_id)

    assert report["scan_summary"]["scan_count"] == 1
    assert report["scan_summary"]["latest_scan_source"] == "sample_logs.jsonl"
    assert report["risk_summary"]["total_findings"] == 4
    assert report["risk_summary"]["counts_by_risk_level"] == {
        "critical": 2,
        "high": 1,
        "medium": 1,
        "low": 0,
    }
    assert report["risk_summary"]["highest_risk_level"] == "critical"
    assert report["data_inventory_summary"]["counts_by_pii_type"]["aadhaar"] == 1
    assert report["data_inventory_summary"]["counts_by_source_type"]["json"] == 4
    assert report["data_inventory_summary"]["sources_scanned"] == ["sample_logs.jsonl"]


def test_top_risks_sorted_correctly(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    report = get_report(client, project_id)

    top_risks = report["top_risks"]
    assert [risk["pii_type"] for risk in top_risks[:3]] == ["aadhaar", "pan", "email"]
    assert top_risks[0]["risk_level"] == "critical"
    assert top_risks[0]["confidence_score"] == 0.98


def test_dsr_summary_counts_statuses_and_types(client: TestClient, project_id: str) -> None:
    create_data_request(client, project_id, request_type="access")
    create_data_request(client, project_id, request_type="deletion", status="completed")

    report = get_report(client, project_id)

    assert report["dsr_summary"]["total_requests"] == 2
    assert report["dsr_summary"]["counts_by_status"]["new"] == 1
    assert report["dsr_summary"]["counts_by_status"]["completed"] == 1
    assert report["dsr_summary"]["counts_by_type"]["access"] == 1
    assert report["dsr_summary"]["counts_by_type"]["deletion"] == 1
    assert report["dsr_summary"]["open_requests"] == 1


def test_overdue_dsr_requests_counted(client: TestClient, project_id: str) -> None:
    create_data_request(client, project_id, due_date="2020-01-01T00:00:00Z")
    create_data_request(client, project_id, request_type="deletion", status="completed", due_date="2020-01-01T00:00:00Z")

    report = get_report(client, project_id)

    assert report["dsr_summary"]["overdue_requests"] == 1


def test_consent_summary_included_correctly(client: TestClient, project_id: str) -> None:
    create_consent_event(client, project_id, status="granted")
    create_consent_event(client, project_id, status="withdrawn", purpose="ai_processing")

    report = get_report(client, project_id)

    assert report["consent_summary"]["total_events"] == 2
    assert report["consent_summary"]["granted_count"] == 1
    assert report["consent_summary"]["withdrawn_count"] == 1
    purposes = {purpose["purpose"]: purpose for purpose in report["consent_summary"]["purposes"]}
    assert purposes["marketing_whatsapp"]["granted_count"] == 1
    assert purposes["ai_processing"]["withdrawn_count"] == 1


def test_readiness_gaps_include_no_scans_if_no_scans_exist(client: TestClient, project_id: str) -> None:
    report = get_report(client, project_id)

    messages = [gap["message"] for gap in report["readiness_gaps"]]
    assert "No scanner uploads exist for this project." in messages


def test_readiness_gaps_include_critical_findings_if_present(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    report = get_report(client, project_id)

    gaps = report["readiness_gaps"]
    assert any(gap["severity"] == "critical" and "critical personal-data findings" in gap["message"] for gap in gaps)


def test_readiness_gaps_include_no_consent_events_if_none_exist(client: TestClient, project_id: str) -> None:
    report = get_report(client, project_id)

    assert any(gap["area"] == "consent" and "No consent events" in gap["message"] for gap in report["readiness_gaps"])


def test_remediation_summary_groups_actions(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    report = get_report(client, project_id)

    actions = report["remediation_summary"]["actions"]
    titles = [action["title"] for action in actions]
    assert "Review Aadhaar/PAN storage and retention" in titles
    assert "Redact personal data before log or prompt ingestion" in titles
    assert report["remediation_summary"]["critical_actions"] >= 1


def test_report_does_not_claim_legal_certification(client: TestClient, project_id: str) -> None:
    report = get_report(client, project_id)
    serialized = str(report).lower()

    assert "certified " + "compliant" not in serialized
    assert "legal compliance " + "guaranteed" not in serialized
    assert "dpdp " + "approved" not in serialized
    assert "not a legal compliance certificate" in report["disclaimer"].lower()
