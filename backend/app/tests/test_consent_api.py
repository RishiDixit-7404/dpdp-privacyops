from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def consent_payload(
    *,
    external_user_id: str = "usr_123",
    purpose: str = "marketing_whatsapp",
    status: str = "granted",
    notice_version: str = "v2.1",
    occurred_at: str = "2026-04-26T10:30:00+05:30",
) -> dict[str, object]:
    return {
        "external_user_id": external_user_id,
        "purpose": purpose,
        "status": status,
        "notice_version": notice_version,
        "source": "web_signup",
        "occurred_at": occurred_at,
        "metadata": {
            "ip_country": "IN",
            "ui_surface": "signup_checkbox",
        },
    }


def create_api_key(client: TestClient, project_id: str, name: str = "Consent writer") -> str:
    response = client.post(f"/projects/{project_id}/api-keys", json={"name": name})
    assert response.status_code == 201
    return str(response.json()["api_key"])


def api_key_headers(client: TestClient, project_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_api_key(client, project_id)}"}


def create_consent_event(
    client: TestClient,
    project_id: str,
    api_key: str | None = None,
    **kwargs: object,
) -> dict[str, object]:
    key = api_key or create_api_key(client, project_id)
    response = client.post(
        f"/projects/{project_id}/consent-events",
        json=consent_payload(**kwargs),
        headers={"Authorization": f"Bearer {key}"},
    )
    assert response.status_code == 201
    return response.json()


def test_create_consent_event(client: TestClient, project_id: str) -> None:
    response = client.post(
        f"/projects/{project_id}/consent-events",
        json=consent_payload(),
        headers=api_key_headers(client, project_id),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["external_user_id"] == "usr_123"
    assert body["purpose"] == "marketing_whatsapp"
    assert body["status"] == "granted"
    assert body["notice_version"] == "v2.1"
    assert body["metadata"] == {"ip_country": "IN", "ui_surface": "signup_checkbox"}


def test_project_not_found_returns_404(client: TestClient) -> None:
    response = client.post(f"/projects/{uuid4()}/consent-events", json=consent_payload())

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_create_consent_event_without_api_key_returns_401(client: TestClient, project_id: str) -> None:
    response = client.post(f"/projects/{project_id}/consent-events", json=consent_payload())

    assert response.status_code == 401
    assert response.json()["detail"] == "Valid project API key required"


def test_invalid_status_rejected(client: TestClient, project_id: str) -> None:
    response = client.post(
        f"/projects/{project_id}/consent-events",
        json=consent_payload(status="pending"),
        headers=api_key_headers(client, project_id),
    )

    assert response.status_code == 422


def test_empty_external_user_id_rejected(client: TestClient, project_id: str) -> None:
    response = client.post(
        f"/projects/{project_id}/consent-events",
        json=consent_payload(external_user_id="  "),
        headers=api_key_headers(client, project_id),
    )

    assert response.status_code == 422


def test_empty_purpose_rejected(client: TestClient, project_id: str) -> None:
    response = client.post(
        f"/projects/{project_id}/consent-events",
        json=consent_payload(purpose="  "),
        headers=api_key_headers(client, project_id),
    )

    assert response.status_code == 422


def test_empty_notice_version_rejected(client: TestClient, project_id: str) -> None:
    response = client.post(
        f"/projects/{project_id}/consent-events",
        json=consent_payload(notice_version="  "),
        headers=api_key_headers(client, project_id),
    )

    assert response.status_code == 422


def test_naive_occurred_at_rejected(client: TestClient, project_id: str) -> None:
    response = client.post(
        f"/projects/{project_id}/consent-events",
        json=consent_payload(occurred_at="2026-04-26T10:30:00"),
        headers=api_key_headers(client, project_id),
    )

    assert response.status_code == 422


def test_metadata_size_limit_enforced(client: TestClient, project_id: str) -> None:
    payload = consent_payload()
    payload["metadata"] = {"large": "x" * (11 * 1024)}

    response = client.post(f"/projects/{project_id}/consent-events", json=payload, headers=api_key_headers(client, project_id))

    assert response.status_code == 422
    assert "x" * 64 not in response.text


def test_list_consent_events_by_project(client: TestClient, project_id: str) -> None:
    create_consent_event(client, project_id, purpose="marketing_whatsapp")
    create_consent_event(client, project_id, purpose="product_analytics", status="withdrawn")

    response = client.get(f"/projects/{project_id}/consent-events")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_filter_by_external_user_id(client: TestClient, project_id: str) -> None:
    create_consent_event(client, project_id, external_user_id="usr_123")
    create_consent_event(client, project_id, external_user_id="usr_456")

    response = client.get(f"/projects/{project_id}/consent-events", params={"external_user_id": "usr_456"})

    assert response.status_code == 200
    assert [item["external_user_id"] for item in response.json()["items"]] == ["usr_456"]


def test_filter_by_purpose(client: TestClient, project_id: str) -> None:
    create_consent_event(client, project_id, purpose="marketing_whatsapp")
    create_consent_event(client, project_id, purpose="ai_processing")

    response = client.get(f"/projects/{project_id}/consent-events", params={"purpose": "ai_processing"})

    assert response.status_code == 200
    assert [item["purpose"] for item in response.json()["items"]] == ["ai_processing"]


def test_filter_by_status(client: TestClient, project_id: str) -> None:
    create_consent_event(client, project_id, status="granted")
    create_consent_event(client, project_id, status="withdrawn")

    response = client.get(f"/projects/{project_id}/consent-events", params={"status": "withdrawn"})

    assert response.status_code == 200
    assert [item["status"] for item in response.json()["items"]] == ["withdrawn"]


def test_pagination_works(client: TestClient, project_id: str) -> None:
    create_consent_event(client, project_id, external_user_id="usr_123")
    create_consent_event(client, project_id, external_user_id="usr_456")

    response = client.get(f"/projects/{project_id}/consent-events", params={"limit": 1, "offset": 0})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["limit"] == 1
    assert body["offset"] == 0
    assert len(body["items"]) == 1


def test_latest_status_returns_most_recent_event(client: TestClient, project_id: str) -> None:
    create_consent_event(
        client,
        project_id,
        status="granted",
        occurred_at="2026-04-26T10:30:00+05:30",
    )
    latest = create_consent_event(
        client,
        project_id,
        status="withdrawn",
        occurred_at="2026-04-27T10:30:00+05:30",
    )

    response = client.get(
        f"/projects/{project_id}/consent-status",
        params={"external_user_id": "usr_123", "purpose": "marketing_whatsapp"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["current_status"] == "withdrawn"
    assert body["latest_event_id"] == latest["id"]


def test_latest_status_uses_created_at_tie_breaker(client: TestClient, project_id: str) -> None:
    occurred_at = "2026-04-26T10:30:00+05:30"
    create_consent_event(client, project_id, status="granted", occurred_at=occurred_at)
    latest = create_consent_event(client, project_id, status="withdrawn", occurred_at=occurred_at)

    response = client.get(
        f"/projects/{project_id}/consent-status",
        params={"external_user_id": "usr_123", "purpose": "marketing_whatsapp"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["current_status"] == "withdrawn"
    assert body["latest_event_id"] == latest["id"]


def test_no_event_status_returns_404(client: TestClient, project_id: str) -> None:
    response = client.get(
        f"/projects/{project_id}/consent-status",
        params={"external_user_id": "usr_missing", "purpose": "marketing_whatsapp"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Consent status not found"


def test_summary_endpoint_returns_counts(client: TestClient, project_id: str) -> None:
    create_consent_event(client, project_id, purpose="marketing_whatsapp", status="granted")
    create_consent_event(client, project_id, purpose="marketing_whatsapp", status="withdrawn")
    create_consent_event(client, project_id, purpose="ai_processing", status="granted")

    response = client.get(f"/projects/{project_id}/consent-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total_events"] == 3
    assert body["granted_count"] == 2
    assert body["withdrawn_count"] == 1
    purposes = {item["purpose"]: item for item in body["purposes"]}
    assert purposes["marketing_whatsapp"]["granted_count"] == 1
    assert purposes["marketing_whatsapp"]["withdrawn_count"] == 1


def test_no_update_or_delete_routes_exist_for_consent_events(client: TestClient, project_id: str) -> None:
    event = create_consent_event(client, project_id)

    patch_response = client.patch(f"/projects/{project_id}/consent-events/{event['id']}", json={"status": "withdrawn"})
    delete_response = client.delete(f"/projects/{project_id}/consent-events/{event['id']}")

    assert patch_response.status_code in {404, 405}
    assert delete_response.status_code in {404, 405}
