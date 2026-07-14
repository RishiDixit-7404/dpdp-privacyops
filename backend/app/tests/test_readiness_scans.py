from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.conftest import scanner_payload


def readiness_scan_payload(project_id: str, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "project_id": project_id,
        "customer_name": "Acme EdTech",
        "customer_segment": "edtech",
        "package_name": "DPDP Technical Readiness Scan",
        "price_inr": 9999,
        "notes": "Demo readiness scan using masked metadata and synthetic findings.",
    }
    payload.update(overrides)
    return payload


def create_readiness_scan(client: TestClient, project_id: str, **overrides: object) -> dict[str, object]:
    response = client.post("/api/readiness-scans", json=readiness_scan_payload(project_id, **overrides))
    assert response.status_code == 201
    return response.json()


def test_create_readiness_scan_defaults_checklist(client: TestClient, project_id: str) -> None:
    response = client.post("/api/readiness-scans", json=readiness_scan_payload(project_id))

    assert response.status_code == 201
    body = response.json()
    assert body["customer_name"] == "Acme EdTech"
    assert body["customer_segment"] == "edtech"
    assert body["package_name"] == "DPDP Technical Readiness Scan"
    assert body["price_inr"] == 9999
    assert body["status"] == "draft"
    assert body["input_checklist"] == {
        "schema_dump": False,
        "masked_csv_exports": False,
        "log_samples": False,
        "privacy_notice": False,
        "third_party_tools": False,
        "ai_prompt_samples": False,
    }


def test_list_readiness_scans(client: TestClient, project_id: str) -> None:
    created = create_readiness_scan(client, project_id)

    response = client.get("/api/readiness-scans")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [created["id"]]


def test_get_readiness_scan(client: TestClient, project_id: str) -> None:
    created = create_readiness_scan(client, project_id)

    response = client.get(f"/api/readiness-scans/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_update_status_and_checklist(client: TestClient, project_id: str) -> None:
    created = create_readiness_scan(client, project_id)

    status_response = client.patch(f"/api/readiness-scans/{created['id']}", json={"status": "inputs_received"})
    checklist_response = client.post(
        f"/api/readiness-scans/{created['id']}/checklist",
        json={
            "schema_dump": True,
            "masked_csv_exports": True,
            "log_samples": True,
        },
    )

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "inputs_received"
    assert checklist_response.status_code == 200
    checklist = checklist_response.json()["input_checklist"]
    assert checklist["schema_dump"] is True
    assert checklist["masked_csv_exports"] is True
    assert checklist["log_samples"] is True
    assert checklist["privacy_notice"] is False


def test_invalid_status_rejected(client: TestClient, project_id: str) -> None:
    response = client.post("/api/readiness-scans", json=readiness_scan_payload(project_id, status="paid"))

    assert response.status_code == 422


def test_obvious_raw_pii_in_notes_rejected(client: TestClient, project_id: str) -> None:
    unsafe_phone = "".join(["98", "765", "432", "10"])
    response = client.post(
        "/api/readiness-scans",
        json=readiness_scan_payload(project_id, notes=f"Customer contact {unsafe_phone}"),
    )

    assert response.status_code == 422
    assert unsafe_phone not in response.text


def test_summary_computation(client: TestClient, project_id: str) -> None:
    scan = create_readiness_scan(
        client,
        project_id,
        status="report_ready",
        input_checklist={
            "schema_dump": True,
            "masked_csv_exports": True,
            "log_samples": True,
            "privacy_notice": True,
            "third_party_tools": True,
            "ai_prompt_samples": True,
        },
    )
    upload = client.post(f"/projects/{project_id}/scans/upload", json=scanner_payload())
    assert upload.status_code == 201
    data_request = client.post(
        f"/projects/{project_id}/data-requests",
        json={
            "request_type": "access",
            "requester_name": None,
            "requester_email": "r***@example.com",
            "requester_identifier": "student_****",
            "request_details": "Safe demo request.",
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
            "metadata": {"seed": "readiness_scan_test"},
        },
    )
    assert consent.status_code == 201

    response = client.get(f"/api/readiness-scans/{scan['id']}/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["package_name"] == "DPDP Technical Readiness Scan"
    assert body["price_inr"] == 9999
    assert body["status"] == "report_ready"
    assert body["checklist_completion_percentage"] == 100
    assert body["linked_project"]["name"] == "Main App"
    assert body["finding_count"] == 4
    assert body["high_or_critical_risk_count"] == 3
    assert body["dsr_request_count"] == 1
    assert body["consent_event_count"] == 1
    assert body["evidence_report_available"] is True
    assert body["next_recommended_action"] == "Review evidence report"


def test_readiness_scan_does_not_require_raw_pii(client: TestClient, project_id: str) -> None:
    response = client.post(
        "/api/readiness-scans",
        json=readiness_scan_payload(
            project_id,
            customer_name="Acme EdTech",
            notes="Demo readiness scan using masked metadata and synthetic findings.",
        ),
    )

    assert response.status_code == 201
