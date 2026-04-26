from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import models
from app.deps import get_db
from app.schemas import ProjectCreate, ProjectResponse


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> models.Project:
    organization = models.Organization(name=payload.organization_name)
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
def list_projects(db: Session = Depends(get_db)) -> list[models.Project]:
    statement = select(models.Project).options(joinedload(models.Project.organization)).order_by(models.Project.created_at.desc())
    return list(db.scalars(statement).all())


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: UUID, db: Session = Depends(get_db)) -> models.Project:
    project = db.scalar(
        select(models.Project)
        .where(models.Project.id == project_id)
        .options(joinedload(models.Project.organization))
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

