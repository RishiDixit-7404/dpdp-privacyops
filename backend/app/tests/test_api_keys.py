from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from app.tests.test_consent_api import consent_payload


def create_api_key(client: TestClient, project_id: str, name: str = "Consent API") -> dict[str, object]:
    response = client.post(f"/projects/{project_id}/api-keys", json={"name": name})
    assert response.status_code == 201
    return response.json()


def create_project(client: TestClient, name: str) -> str:
    response = client.post(
        "/projects",
        json={
            "organization_name": "Acme",
            "project_name": name,
            "description": "Test project",
        },
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_create_api_key_returns_raw_key_once_and_stores_hash(client: TestClient, project_id: str, db_session: Session) -> None:
    body = create_api_key(client, project_id)

    assert body["name"] == "Consent API"
    assert str(body["api_key"]).startswith("dpdp_live_")
    assert body["key_prefix"] == str(body["api_key"])[:18]
    assert "key_hash" not in body

    stored_key = db_session.get(models.ProjectApiKey, UUID(str(body["id"])))
    assert stored_key is not None
    assert stored_key.key_hash
    assert stored_key.key_hash != body["api_key"]


def test_list_api_keys_never_exposes_raw_key_or_hash(client: TestClient, project_id: str) -> None:
    created = create_api_key(client, project_id)

    response = client.get(f"/projects/{project_id}/api-keys")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["id"] == created["id"]
    assert body[0]["key_prefix"] == created["key_prefix"]
    assert "api_key" not in body[0]
    assert "key_hash" not in body[0]


def test_revoke_api_key_sets_revoked_at_and_does_not_delete(client: TestClient, project_id: str) -> None:
    created = create_api_key(client, project_id)

    response = client.post(f"/projects/{project_id}/api-keys/{created['id']}/revoke")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["revoked_at"] is not None

    list_response = client.get(f"/projects/{project_id}/api-keys")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == created["id"]


def test_consent_write_with_valid_api_key_succeeds_and_updates_last_used(
    client: TestClient,
    project_id: str,
) -> None:
    created = create_api_key(client, project_id)

    response = client.post(
        f"/projects/{project_id}/consent-events",
        json=consent_payload(),
        headers={"X-DPDP-API-Key": str(created["api_key"])},
    )

    assert response.status_code == 201
    list_response = client.get(f"/projects/{project_id}/api-keys")
    assert list_response.status_code == 200
    assert list_response.json()[0]["last_used_at"] is not None


def test_consent_write_with_revoked_api_key_fails(client: TestClient, project_id: str) -> None:
    created = create_api_key(client, project_id)
    revoke = client.post(f"/projects/{project_id}/api-keys/{created['id']}/revoke")
    assert revoke.status_code == 200

    response = client.post(
        f"/projects/{project_id}/consent-events",
        json=consent_payload(),
        headers={"Authorization": f"Bearer {created['api_key']}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Valid project API key required"


def test_consent_write_with_api_key_from_another_project_fails(client: TestClient, project_id: str) -> None:
    other_project_id = create_project(client, "Other App")
    other_key = create_api_key(client, other_project_id)

    response = client.post(
        f"/projects/{project_id}/consent-events",
        json=consent_payload(),
        headers={"Authorization": f"Bearer {other_key['api_key']}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Valid project API key required"
