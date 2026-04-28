from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.tests.conftest import register_and_login


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_project_for_user(client: TestClient, token: str, project_name: str, organization_name: str) -> str:
    response = client.post(
        "/projects",
        json={
            "organization_name": organization_name,
            "project_name": project_name,
            "description": "Access test",
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_project_list_requires_auth(client: TestClient) -> None:
    response = client.get("/projects")

    assert response.status_code == 401


def test_user_cannot_access_another_organizations_project(client: TestClient) -> None:
    owner_token = register_and_login(client, email="owner-a@example.com")
    project_id = create_project_for_user(client, owner_token, "Owner A Project", "Owner A Org")

    other_token = register_and_login(client, email="owner-b@example.com")
    response = client.get(f"/projects/{project_id}", headers=auth_headers(other_token))

    assert response.status_code == 403
    assert response.json()["detail"] == "Project access denied"


def test_owner_can_create_api_key(client: TestClient, project_id: str) -> None:
    response = client.post(f"/projects/{project_id}/api-keys", json={"name": "Owner key"})

    assert response.status_code == 201
    assert response.json()["api_key"].startswith("dpdp_live_")


def test_member_cannot_revoke_api_key(client: TestClient, project_id: str, db_session: Session) -> None:
    created = client.post(f"/projects/{project_id}/api-keys", json={"name": "Owner key"})
    assert created.status_code == 201

    member_token = register_and_login(client, email="member@example.com")
    project = db_session.get(models.Project, UUID(project_id))
    member = db_session.scalar(select(models.User).where(models.User.email == "member@example.com"))
    assert project is not None
    assert member is not None
    db_session.add(
        models.OrganizationMembership(
            user_id=member.id,
            organization_id=project.organization_id,
            role="member",
        )
    )
    db_session.commit()

    response = client.post(
        f"/projects/{project_id}/api-keys/{created.json()['id']}/revoke",
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403
