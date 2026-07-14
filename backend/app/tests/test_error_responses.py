from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.tests.conftest import scanner_payload


RAW_ERROR_VALUE = "rahul.raw@example.com"


def assert_json_error_without_raw_pii(response, expected_status: int) -> None:
    assert response.status_code == expected_status
    assert response.headers["content-type"].startswith("application/json")
    assert RAW_ERROR_VALUE not in response.text


def test_project_not_found_on_upload_returns_404_json(client: TestClient) -> None:
    payload = scanner_payload()
    payload["source"] = RAW_ERROR_VALUE

    response = client.post(f"/projects/{uuid4()}/scans/upload", json=payload)

    assert_json_error_without_raw_pii(response, 404)
    assert response.json()["detail"] == "Project not found"


def test_invalid_scanner_payload_returns_sanitized_422_json(client: TestClient, project_id: str) -> None:
    payload = scanner_payload()
    payload["findings"][0]["confidence_score"] = 1.5  # type: ignore
    payload["findings"][0]["masked_examples"] = [RAW_ERROR_VALUE]  # type: ignore

    response = client.post(f"/projects/{project_id}/scans/upload", json=payload)

    assert_json_error_without_raw_pii(response, 422)
    assert "detail" in response.json()


def test_raw_pii_uploaded_true_returns_sanitized_422_json(client: TestClient, project_id: str) -> None:
    payload = scanner_payload()
    payload["raw_pii_uploaded"] = True
    payload["source"] = RAW_ERROR_VALUE

    response = client.post(f"/projects/{project_id}/scans/upload", json=payload)

    assert_json_error_without_raw_pii(response, 422)


def test_invalid_finding_filter_enum_returns_sanitized_422_json(client: TestClient, project_id: str) -> None:
    response = client.get(
        f"/projects/{project_id}/findings",
        params={"risk_level": "critical", "source_type": RAW_ERROR_VALUE},
    )

    assert_json_error_without_raw_pii(response, 422)


def test_scan_not_found_returns_404_json(client: TestClient) -> None:
    response = client.get(f"/scans/{uuid4()}")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["detail"] == "Scan not found"


def test_project_not_found_returns_404_json(client: TestClient) -> None:
    response = client.get(f"/projects/{uuid4()}")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["detail"] == "Project not found"


def test_duplicate_scanner_scan_id_returns_409_json(client: TestClient, project_id: str) -> None:
    first = client.post(f"/projects/{project_id}/scans/upload", json=scanner_payload())
    duplicate_payload = scanner_payload()
    duplicate_payload["source"] = RAW_ERROR_VALUE

    response = client.post(f"/projects/{project_id}/scans/upload", json=duplicate_payload)

    assert first.status_code == 201
    assert_json_error_without_raw_pii(response, 409)
    assert response.json()["detail"] == "scanner_scan_id already ingested"
