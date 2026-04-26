from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models
from app.deps import get_db
from app.schemas import (
    ConsentEventCreate,
    ConsentEventListResponse,
    ConsentEventResponse,
    ConsentPurposeSummary,
    ConsentStatus,
    ConsentStatusResponse,
    ConsentSummaryResponse,
)


router = APIRouter(tags=["consent"])


def _get_project_or_404(db: Session, project_id: UUID) -> models.Project:
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/{project_id}/consent-events", response_model=ConsentEventResponse, status_code=201)
def create_consent_event(
    project_id: UUID,
    payload: ConsentEventCreate,
    db: Session = Depends(get_db),
) -> models.ConsentEvent:
    _get_project_or_404(db, project_id)
    event = models.ConsentEvent(
        project_id=project_id,
        external_user_id=payload.external_user_id,
        purpose=payload.purpose,
        status=payload.status.value,
        notice_version=payload.notice_version,
        source=payload.source,
        occurred_at=payload.occurred_at,
        event_metadata=payload.metadata,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/projects/{project_id}/consent-events", response_model=ConsentEventListResponse)
def list_consent_events(
    project_id: UUID,
    external_user_id: str | None = Query(default=None),
    purpose: str | None = Query(default=None),
    status: ConsentStatus | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ConsentEventListResponse:
    _get_project_or_404(db, project_id)
    filters = [models.ConsentEvent.project_id == project_id]
    if external_user_id:
        filters.append(models.ConsentEvent.external_user_id == external_user_id)
    if purpose:
        filters.append(models.ConsentEvent.purpose == purpose)
    if status is not None:
        filters.append(models.ConsentEvent.status == status.value)

    total = db.scalar(select(func.count()).select_from(models.ConsentEvent).where(*filters)) or 0
    statement = (
        select(models.ConsentEvent)
        .where(*filters)
        .order_by(models.ConsentEvent.occurred_at.desc(), models.ConsentEvent.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = list(db.scalars(statement).all())
    return ConsentEventListResponse(
        items=[ConsentEventResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/projects/{project_id}/consent-status", response_model=ConsentStatusResponse)
def get_consent_status(
    project_id: UUID,
    external_user_id: str = Query(min_length=1),
    purpose: str = Query(min_length=1),
    db: Session = Depends(get_db),
) -> ConsentStatusResponse:
    _get_project_or_404(db, project_id)
    event = db.scalar(
        select(models.ConsentEvent)
        .where(
            models.ConsentEvent.project_id == project_id,
            models.ConsentEvent.external_user_id == external_user_id,
            models.ConsentEvent.purpose == purpose,
        )
        .order_by(models.ConsentEvent.occurred_at.desc(), models.ConsentEvent.created_at.desc())
        .limit(1)
    )
    if event is None:
        raise HTTPException(status_code=404, detail="Consent status not found")

    return ConsentStatusResponse(
        project_id=event.project_id,
        external_user_id=event.external_user_id,
        purpose=event.purpose,
        current_status=ConsentStatus(event.status),
        notice_version=event.notice_version,
        source=event.source,
        occurred_at=event.occurred_at,
        latest_event_id=event.id,
    )


@router.get("/projects/{project_id}/consent-summary", response_model=ConsentSummaryResponse)
def get_consent_summary(project_id: UUID, db: Session = Depends(get_db)) -> ConsentSummaryResponse:
    _get_project_or_404(db, project_id)
    events = list(db.scalars(select(models.ConsentEvent).where(models.ConsentEvent.project_id == project_id)).all())
    purpose_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"granted": 0, "withdrawn": 0})
    latest_by_purpose: dict[str, datetime] = {}

    for event in events:
        purpose_counts[event.purpose][event.status] += 1
        current_latest = latest_by_purpose.get(event.purpose)
        if current_latest is None or event.occurred_at > current_latest:
            latest_by_purpose[event.purpose] = event.occurred_at

    purposes = [
        ConsentPurposeSummary(
            purpose=purpose,
            granted_count=counts["granted"],
            withdrawn_count=counts["withdrawn"],
            latest_event_at=latest_by_purpose.get(purpose),
        )
        for purpose, counts in sorted(purpose_counts.items())
    ]
    granted_count = sum(1 for event in events if event.status == "granted")
    withdrawn_count = sum(1 for event in events if event.status == "withdrawn")
    return ConsentSummaryResponse(
        total_events=len(events),
        granted_count=granted_count,
        withdrawn_count=withdrawn_count,
        purposes=purposes,
    )
