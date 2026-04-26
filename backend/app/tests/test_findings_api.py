from fastapi.testclient import TestClient

from app.tests.conftest import scanner_payload


def upload_scan(client: TestClient, project_id: str) -> str:
    response = client.post(f"/projects/{project_id}/scans/upload", json=scanner_payload())
    assert response.status_code == 201
    return response.json()["id"]


def test_findings_are_persisted(client: TestClient, project_id: str) -> None:
    scan_id = upload_scan(client, project_id)

    response = client.get(f"/scans/{scan_id}/findings")

    assert response.status_code == 200
    payload = response.json()
    findings = payload["items"]
    assert payload["total"] == 4
    assert payload["limit"] == 100
    assert payload["offset"] == 0
    assert len(findings) == 4
    assert {finding["pii_type"] for finding in findings} == {"email", "aadhaar", "pan", "person_name"}


def test_findings_api_filters_by_risk_level(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    response = client.get(f"/projects/{project_id}/findings", params={"risk_level": "critical"})

    assert response.status_code == 200
    findings = response.json()["items"]
    assert len(findings) == 2
    assert all(finding["risk_level"] == "critical" for finding in findings)


def test_findings_api_filters_by_pii_type(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    response = client.get(f"/projects/{project_id}/findings", params={"pii_type": "email"})

    assert response.status_code == 200
    findings = response.json()["items"]
    assert len(findings) == 1
    assert findings[0]["pii_type"] == "email"


def test_findings_api_filters_by_source_type_and_scan_id(client: TestClient, project_id: str) -> None:
    scan_id = upload_scan(client, project_id)

    response = client.get(
        f"/projects/{project_id}/findings",
        params={"source_type": "json", "scan_id": scan_id},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 4
    assert len(payload["items"]) == 4


def test_findings_sorted_by_risk_severity_then_confidence(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    response = client.get(f"/projects/{project_id}/findings")

    assert response.status_code == 200
    findings = response.json()["items"]
    assert [finding["pii_type"] for finding in findings] == ["aadhaar", "pan", "email", "person_name"]
    assert [finding["risk_level"] for finding in findings] == ["critical", "critical", "high", "medium"]


def test_findings_api_paginates_project_findings(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    response = client.get(f"/projects/{project_id}/findings", params={"limit": 2, "offset": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 4
    assert payload["limit"] == 2
    assert payload["offset"] == 1
    assert len(payload["items"]) == 2


def test_findings_api_paginates_scan_findings(client: TestClient, project_id: str) -> None:
    scan_id = upload_scan(client, project_id)

    response = client.get(f"/scans/{scan_id}/findings", params={"limit": 1, "offset": 2})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 4
    assert payload["limit"] == 1
    assert payload["offset"] == 2
    assert len(payload["items"]) == 1
