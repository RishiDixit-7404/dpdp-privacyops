from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.deps import get_current_user, get_db
from app.schemas import ApiKeyCreate, ApiKeyCreateResponse, ApiKeyResponse
from app.services.access_control import ADMIN_ROLES, require_project_access
from app.services.api_keys import create_project_api_key


router = APIRouter(prefix="/projects/{project_id}/api-keys", tags=["api keys"])


def _get_project_or_404(db: Session, project_id: UUID) -> models.Project:
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ApiKeyCreateResponse, status_code=201)
def create_api_key(
    project_id: UUID,
    payload: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> ApiKeyCreateResponse:
    _get_project_or_404(db, project_id)
    require_project_access(db, current_user, project_id, ADMIN_ROLES)
    api_key, raw_key = create_project_api_key(db, project_id, payload.name)
    response = ApiKeyResponse.model_validate(api_key)
    return ApiKeyCreateResponse(**response.model_dump(), api_key=raw_key)


@router.get("", response_model=list[ApiKeyResponse])
def list_api_keys(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[models.ProjectApiKey]:
    _get_project_or_404(db, project_id)
    require_project_access(db, current_user, project_id, ADMIN_ROLES)
    statement = (
        select(models.ProjectApiKey)
        .where(models.ProjectApiKey.project_id == project_id)
        .order_by(models.ProjectApiKey.created_at.desc())
    )
    return list(db.scalars(statement).all())


@router.post("/{api_key_id}/revoke", response_model=ApiKeyResponse)
def revoke_api_key(
    project_id: UUID,
    api_key_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.ProjectApiKey:
    _get_project_or_404(db, project_id)
    require_project_access(db, current_user, project_id, ADMIN_ROLES)
    api_key = db.get(models.ProjectApiKey, api_key_id)
    if api_key is None or api_key.project_id != project_id:
        raise HTTPException(status_code=404, detail="API key not found")
    if api_key.revoked_at is None:
        api_key.revoked_at = models.utc_now()
        db.commit()
        db.refresh(api_key)
    return api_key
