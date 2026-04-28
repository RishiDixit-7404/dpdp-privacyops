from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import models
from app.deps import get_current_user, get_db
from app.schemas import ProjectCreate, ProjectResponse
from app.services.access_control import ADMIN_ROLES, require_project_access


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Project:
    membership = db.scalar(
        select(models.OrganizationMembership)
        .join(models.Organization)
        .where(
            models.OrganizationMembership.user_id == current_user.id,
            models.Organization.name == payload.organization_name,
        )
        .order_by(models.OrganizationMembership.created_at.asc())
    )
    if membership is not None and membership.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Project access denied")

    if membership is not None:
        organization = membership.organization
    else:
        organization = models.Organization(name=payload.organization_name)
        db.add(organization)
        db.flush()
        db.add(
            models.OrganizationMembership(
                user_id=current_user.id,
                organization_id=organization.id,
                role="owner",
            )
        )

    project = models.Project(
        organization=organization,
        name=payload.project_name,
        description=payload.description,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[models.Project]:
    statement = (
        select(models.Project)
        .join(models.OrganizationMembership, models.Project.organization_id == models.OrganizationMembership.organization_id)
        .where(models.OrganizationMembership.user_id == current_user.id)
        .options(joinedload(models.Project.organization))
        .order_by(models.Project.created_at.desc())
    )
    return list(db.scalars(statement).all())


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Project:
    project = db.scalar(
        select(models.Project)
        .where(models.Project.id == project_id)
        .options(joinedload(models.Project.organization))
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    require_project_access(db, current_user, project_id)
    return project

