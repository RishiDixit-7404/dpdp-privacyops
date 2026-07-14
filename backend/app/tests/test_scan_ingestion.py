from fastapi.testclient import TestClient

from app.tests.conftest import scanner_payload


def test_project_creation_works(client: TestClient) -> None:
    response = client.post(
        "/projects",
        json={
            "organization_name": "Example Org",
            "project_name": "Customer App",
            "description": "MVP project",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Customer App"
    assert payload["description"] == "MVP project"
    assert payload["organization"]["name"] == "Example Org"


def test_scanner_upload_persists_scan_and_summary(client: TestClient, project_id: str) -> None:
    response = client.post(f"/projects/{project_id}/scans/upload", json=scanner_payload())

    assert response.status_code == 201
    payload = response.json()
    assert payload["scanner_scan_id"] == "scanner-scan-001"
    assert payload["scan_type"] == "json"
    assert payload["raw_pii_uploaded"] is False
    assert payload["summary"]["total_findings"] == 4
    assert payload["summary"]["counts_by_risk_level"] == {
        "critical": 2,
        "high": 1,
        "medium": 1,
        "low": 0,
    }
    assert payload["summary"]["critical_count"] == 2
    assert payload["summary"]["high_count"] == 1
    assert payload["summary"]["counts_by_pii_type"]["aadhaar"] == 1

    scans_response = client.get(f"/projects/{project_id}/scans")
    assert scans_response.status_code == 200
    assert len(scans_response.json()) == 1


def test_upload_rejects_raw_pii_uploaded_true(client: TestClient, project_id: str) -> None:
    payload = scanner_payload()
    payload["raw_pii_uploaded"] = True

    response = client.post(f"/projects/{project_id}/scans/upload", json=payload)

    assert response.status_code == 422


def test_scan_detail_summary_matches_upload_summary(client: TestClient, project_id: str) -> None:
    upload_response = client.post(f"/projects/{project_id}/scans/upload", json=scanner_payload())
    assert upload_response.status_code == 201

    detail_response = client.get(f"/scans/{upload_response.json()['id']}")

    assert detail_response.status_code == 200
    assert detail_response.json()["summary"] == upload_response.json()["summary"]


def test_duplicate_scanner_scan_id_returns_409(client: TestClient, project_id: str) -> None:
    first_response = client.post(f"/projects/{project_id}/scans/upload", json=scanner_payload())
    second_response = client.post(f"/projects/{project_id}/scans/upload", json=scanner_payload())

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_masked_examples_max_three_validation(client: TestClient, project_id: str) -> None:
    payload = scanner_payload()
    payload["findings"][0]["masked_examples"] = ["one", "two", "three", "four"]  # type: ignore

    response = client.post(f"/projects/{project_id}/scans/upload", json=payload)

    assert response.status_code == 422


def test_invalid_confidence_score_rejected(client: TestClient, project_id: str) -> None:
    payload = scanner_payload()
    payload["findings"][0]["confidence_score"] = 1.1  # type: ignore

    response = client.post(f"/projects/{project_id}/scans/upload", json=payload)

    assert response.status_code == 422


def test_invalid_risk_level_rejected(client: TestClient, project_id: str) -> None:
    payload = scanner_payload()
    payload["findings"][0]["risk_level"] = "severe"  # type: ignore

    response = client.post(f"/projects/{project_id}/scans/upload", json=payload)

    assert response.status_code == 422
