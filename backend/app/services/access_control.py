from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


READ_ROLES = {"owner", "admin", "member"}
ADMIN_ROLES = {"owner", "admin"}


@dataclass(frozen=True)
class ProjectAccess:
    project: models.Project
    membership: models.OrganizationMembership


def membership_for_organization(
    db: Session,
    user: models.User,
    organization_id: UUID,
) -> models.OrganizationMembership | None:
    return db.scalar(
        select(models.OrganizationMembership).where(
            models.OrganizationMembership.user_id == user.id,
            models.OrganizationMembership.organization_id == organization_id,
        )
    )


def require_organization_role(
    db: Session,
    user: models.User,
    organization_id: UUID,
    allowed_roles: set[str] = READ_ROLES,
) -> models.OrganizationMembership:
    membership = membership_for_organization(db, user, organization_id)
    if membership is None or membership.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Project access denied")
    return membership


def require_project_access(
    db: Session,
    user: models.User,
    project_id: UUID,
    allowed_roles: set[str] = READ_ROLES,
) -> ProjectAccess:
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    membership = require_organization_role(db, user, project.organization_id, allowed_roles)
    return ProjectAccess(project=project, membership=membership)


def require_scan_access(
    db: Session,
    user: models.User,
    scan_id: UUID,
    allowed_roles: set[str] = READ_ROLES,
) -> models.Scan:
    scan = db.get(models.Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    require_project_access(db, user, scan.project_id, allowed_roles)
    return scan


def require_data_request_access(
    db: Session,
    user: models.User,
    request_id: UUID,
    allowed_roles: set[str] = READ_ROLES,
) -> models.DataRequest:
    data_request = db.get(models.DataRequest, request_id)
    if data_request is None:
        raise HTTPException(status_code=404, detail="Data request not found")
    require_project_access(db, user, data_request.project_id, allowed_roles)
    return data_request
