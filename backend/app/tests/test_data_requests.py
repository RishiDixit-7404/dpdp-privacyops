from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def request_payload(request_type: str = "access") -> dict[str, object]:
    return {
        "request_type": request_type,
        "requester_name": "Rahul Sharma",
        "requester_email": "rahul@example.com",
        "requester_identifier": "usr_123",
        "request_details": "Please send me a copy of my data.",
    }


def create_data_request(client: TestClient, project_id: str, request_type: str = "access") -> dict[str, object]:
    response = client.post(f"/projects/{project_id}/data-requests", json=request_payload(request_type))
    assert response.status_code == 201
    return response.json()


def test_create_data_request(client: TestClient, project_id: str) -> None:
    payload = request_payload("deletion")

    response = client.post(f"/projects/{project_id}/data-requests", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["request_type"] == "deletion"
    assert body["status"] == "new"
    assert body["requester_email"] == "rahul@example.com"
    assert body["completed_at"] is None


def test_public_intake_creates_request_and_returns_minimal_response(client: TestClient, project_id: str) -> None:
    response = client.post(f"/public/projects/{project_id}/data-requests", json=request_payload("correction"))

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"request_id", "status", "message"}
    assert body["status"] == "new"
    assert body["message"] == "Your request has been received."

    detail = client.get(f"/data-requests/{body['request_id']}")
    assert detail.status_code == 200
    assert detail.json()["request_type"] == "correction"


def test_list_data_requests_by_project_and_filters(client: TestClient, project_id: str) -> None:
    access_request = create_data_request(client, project_id, "access")
    deletion_request = create_data_request(client, project_id, "deletion")
    update = client.patch(f"/data-requests/{deletion_request['id']}", json={"status": "in_progress"})
    assert update.status_code == 200

    list_response = client.get(f"/projects/{project_id}/data-requests")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 2

    status_response = client.get(f"/projects/{project_id}/data-requests", params={"status": "in_progress"})
    assert status_response.status_code == 200
    assert [item["id"] for item in status_response.json()["items"]] == [deletion_request["id"]]

    type_response = client.get(f"/projects/{project_id}/data-requests", params={"request_type": "access"})
    assert type_response.status_code == 200
    assert [item["id"] for item in type_response.json()["items"]] == [access_request["id"]]


def test_get_request_details_includes_notes_and_audit_events(client: TestClient, project_id: str) -> None:
    data_request = create_data_request(client, project_id)
    note_response = client.post(
        f"/data-requests/{data_request['id']}/notes",
        json={"note": "Verified requester email manually.", "created_by": "admin"},
    )
    assert note_response.status_code == 201

    response = client.get(f"/data-requests/{data_request['id']}")

    assert response.status_code == 200
    body = response.json()
    assert len(body["notes"]) == 1
    assert body["notes"][0]["note"] == "Verified requester email manually."
    event_types = [event["event_type"] for event in body["audit_events"]]
    assert "created" in event_types
    assert "note_added" in event_types


def test_status_update_creates_audit_event(client: TestClient, project_id: str) -> None:
    data_request = create_data_request(client, project_id)

    response = client.patch(f"/data-requests/{data_request['id']}", json={"status": "verifying"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "verifying"
    event_types = [event["event_type"] for event in body["audit_events"]]
    assert "status_changed" in event_types


def test_assigned_to_update_creates_audit_event(client: TestClient, project_id: str) -> None:
    data_request = create_data_request(client, project_id)

    response = client.patch(f"/data-requests/{data_request['id']}", json={"assigned_to": "ops-owner"})

    assert response.status_code == 200
    body = response.json()
    assert body["assigned_to"] == "ops-owner"
    assert "assigned" in [event["event_type"] for event in body["audit_events"]]


def test_due_date_update_creates_audit_event(client: TestClient, project_id: str) -> None:
    data_request = create_data_request(client, project_id)

    response = client.patch(
        f"/data-requests/{data_request['id']}",
        json={"due_date": "2026-05-10T10:00:00Z"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["due_date"] == "2026-05-10T10:00:00Z"
    assert "due_date_changed" in [event["event_type"] for event in body["audit_events"]]


def test_completed_status_sets_completed_at(client: TestClient, project_id: str) -> None:
    data_request = create_data_request(client, project_id)

    response = client.patch(f"/data-requests/{data_request['id']}", json={"status": "completed"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["completed_at"] is not None
    assert "completed" in [event["event_type"] for event in body["audit_events"]]


def test_rejected_status_creates_rejected_audit_event(client: TestClient, project_id: str) -> None:
    data_request = create_data_request(client, project_id)

    response = client.patch(f"/data-requests/{data_request['id']}", json={"status": "rejected"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert "rejected" in [event["event_type"] for event in body["audit_events"]]


def test_add_note_creates_note_and_audit_event(client: TestClient, project_id: str) -> None:
    data_request = create_data_request(client, project_id)

    response = client.post(
        f"/data-requests/{data_request['id']}/notes",
        json={"note": "Checked account ownership.", "created_by": "admin"},
    )

    assert response.status_code == 201
    assert response.json()["note"] == "Checked account ownership."

    detail = client.get(f"/data-requests/{data_request['id']}")
    assert detail.status_code == 200
    assert "note_added" in [event["event_type"] for event in detail.json()["audit_events"]]


def test_invalid_request_type_rejected(client: TestClient, project_id: str) -> None:
    response = client.post(f"/projects/{project_id}/data-requests", json=request_payload("export"))

    assert response.status_code == 422


def test_invalid_status_rejected(client: TestClient, project_id: str) -> None:
    data_request = create_data_request(client, project_id)

    response = client.patch(f"/data-requests/{data_request['id']}", json={"status": "waiting"})

    assert response.status_code == 422


def test_project_not_found_returns_404(client: TestClient, project_id: str) -> None:
    missing_project_id = str(uuid4())

    response = client.post(f"/projects/{missing_project_id}/data-requests", json=request_payload())

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_request_not_found_returns_404(client: TestClient, project_id: str) -> None:
    missing_request_id = str(uuid4())

    response = client.get(f"/data-requests/{missing_request_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Data request not found"


def test_pagination_works(client: TestClient, project_id: str) -> None:
    first = create_data_request(client, project_id, "access")
    second = create_data_request(client, project_id, "grievance")

    response = client.get(f"/projects/{project_id}/data-requests", params={"limit": 1, "offset": 0})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["limit"] == 1
    assert body["offset"] == 0
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] in {first["id"], second["id"]}
