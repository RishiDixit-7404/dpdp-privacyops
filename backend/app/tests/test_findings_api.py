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
    findings = response.json()
    assert len(findings) == 4
    assert {finding["pii_type"] for finding in findings} == {"email", "aadhaar", "pan", "person_name"}


def test_findings_api_filters_by_risk_level(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    response = client.get(f"/projects/{project_id}/findings", params={"risk_level": "critical"})

    assert response.status_code == 200
    findings = response.json()
    assert len(findings) == 2
    assert all(finding["risk_level"] == "critical" for finding in findings)


def test_findings_api_filters_by_pii_type(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    response = client.get(f"/projects/{project_id}/findings", params={"pii_type": "email"})

    assert response.status_code == 200
    findings = response.json()
    assert len(findings) == 1
    assert findings[0]["pii_type"] == "email"


def test_findings_api_filters_by_source_type_and_scan_id(client: TestClient, project_id: str) -> None:
    scan_id = upload_scan(client, project_id)

    response = client.get(
        f"/projects/{project_id}/findings",
        params={"source_type": "json", "scan_id": scan_id},
    )

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_findings_sorted_by_risk_severity_then_confidence(client: TestClient, project_id: str) -> None:
    upload_scan(client, project_id)

    response = client.get(f"/projects/{project_id}/findings")

    assert response.status_code == 200
    findings = response.json()
    assert [finding["pii_type"] for finding in findings] == ["aadhaar", "pan", "email", "person_name"]
    assert [finding["risk_level"] for finding in findings] == ["critical", "critical", "high", "medium"]

