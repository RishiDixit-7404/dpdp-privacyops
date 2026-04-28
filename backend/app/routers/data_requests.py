from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.deps import get_current_user, get_db
from app.schemas import (
    DataRequestAuditEventResponse,
    DataRequestCreate,
    DataRequestDetailResponse,
    DataRequestListResponse,
    DataRequestNoteCreate,
    DataRequestNoteResponse,
    DataRequestResponse,
    DataRequestStatus,
    DataRequestType,
    DataRequestUpdate,
    PublicDataRequestConfirmation,
)
from app.services.access_control import require_data_request_access, require_project_access


router = APIRouter(tags=["data requests"])


def _get_project_or_404(db: Session, project_id: UUID) -> models.Project:
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_data_request_or_404(db: Session, request_id: UUID) -> models.DataRequest:
    data_request = db.scalar(
        select(models.DataRequest)
        .where(models.DataRequest.id == request_id)
        .options(
            selectinload(models.DataRequest.notes),
            selectinload(models.DataRequest.audit_events),
        )
    )
    if data_request is None:
        raise HTTPException(status_code=404, detail="Data request not found")
    return data_request


def _add_audit_event(
    db: Session,
    data_request_id: UUID,
    event_type: str,
    message: str,
    metadata: dict[str, object] | None = None,
) -> models.DataRequestAuditEvent:
    event = models.DataRequestAuditEvent(
        data_request_id=data_request_id,
        event_type=event_type,
        message=message,
        event_metadata=metadata,
    )
    db.add(event)
    return event


def _create_data_request(db: Session, project_id: UUID, payload: DataRequestCreate) -> models.DataRequest:
    _get_project_or_404(db, project_id)
    data_request = models.DataRequest(
        project_id=project_id,
        request_type=payload.request_type.value,
        status="new",
        requester_name=payload.requester_name,
        requester_email=payload.requester_email,
        requester_identifier=payload.requester_identifier,
        request_details=payload.request_details,
        due_date=payload.due_date,
        assigned_to=payload.assigned_to,
    )
    db.add(data_request)
    db.flush()
    _add_audit_event(
        db,
        data_request.id,
        "created",
        "User Data Request created.",
        {"request_type": payload.request_type.value},
    )
    if payload.assigned_to:
        _add_audit_event(db, data_request.id, "assigned", "Request assigned.", {"assigned_to": payload.assigned_to})
    if payload.due_date:
        _add_audit_event(db, data_request.id, "due_date_changed", "Due date set.", {"due_date": payload.due_date.isoformat()})
    db.commit()
    db.expire_all()
    return _get_data_request_or_404(db, data_request.id)


@router.post("/projects/{project_id}/data-requests", response_model=DataRequestResponse, status_code=201)
def create_data_request(
    project_id: UUID,
    payload: DataRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.DataRequest:
    require_project_access(db, current_user, project_id)
    return _create_data_request(db, project_id, payload)


@router.post("/public/projects/{project_id}/data-requests", response_model=PublicDataRequestConfirmation, status_code=201)
def create_public_data_request(
    project_id: UUID,
    payload: DataRequestCreate,
    db: Session = Depends(get_db),
) -> PublicDataRequestConfirmation:
    data_request = _create_data_request(db, project_id, payload)
    return PublicDataRequestConfirmation(
        request_id=data_request.id,
        status="new",
        message="Your request has been received.",
    )


@router.get("/projects/{project_id}/data-requests", response_model=DataRequestListResponse)
def list_project_data_requests(
    project_id: UUID,
    status: DataRequestStatus | None = Query(default=None),
    request_type: DataRequestType | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> DataRequestListResponse:
    require_project_access(db, current_user, project_id)

    filters = [models.DataRequest.project_id == project_id]
    if status is not None:
        filters.append(models.DataRequest.status == status.value)
    if request_type is not None:
        filters.append(models.DataRequest.request_type == request_type.value)

    total = db.scalar(select(func.count()).select_from(models.DataRequest).where(*filters)) or 0
    statement = (
        select(models.DataRequest)
        .where(*filters)
        .order_by(models.DataRequest.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = list(db.scalars(statement).all())
    return DataRequestListResponse(
        items=[DataRequestResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/data-requests/{request_id}", response_model=DataRequestDetailResponse)
def get_data_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.DataRequest:
    require_data_request_access(db, current_user, request_id)
    return _get_data_request_or_404(db, request_id)


@router.patch("/data-requests/{request_id}", response_model=DataRequestDetailResponse)
def update_data_request(
    request_id: UUID,
    payload: DataRequestUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.DataRequest:
    require_data_request_access(db, current_user, request_id)
    data_request = _get_data_request_or_404(db, request_id)
    changes = payload.model_dump(exclude_unset=True)

    if "status" in changes and payload.status is not None and data_request.status != payload.status.value:
        old_status = data_request.status
        data_request.status = payload.status.value
        _add_audit_event(
            db,
            data_request.id,
            "status_changed",
            f"Status changed from {old_status} to {payload.status.value}.",
            {"from": old_status, "to": payload.status.value},
        )
        if payload.status == DataRequestStatus.completed:
            data_request.completed_at = models.utc_now()
            _add_audit_event(db, data_request.id, "completed", "Request marked completed.")
        elif payload.status == DataRequestStatus.rejected:
            data_request.completed_at = None
            _add_audit_event(db, data_request.id, "rejected", "Request rejected.")
        elif old_status in {"completed", "rejected"}:
            data_request.completed_at = None

    if "assigned_to" in changes and data_request.assigned_to != payload.assigned_to:
        data_request.assigned_to = payload.assigned_to
        _add_audit_event(
            db,
            data_request.id,
            "assigned",
            "Assignment changed.",
            {"assigned_to": payload.assigned_to},
        )

    if "due_date" in changes and data_request.due_date != payload.due_date:
        data_request.due_date = payload.due_date
        due_date_value = payload.due_date.isoformat() if isinstance(payload.due_date, datetime) else None
        _add_audit_event(
            db,
            data_request.id,
            "due_date_changed",
            "Due date changed.",
            {"due_date": due_date_value},
        )

    if "request_details" in changes:
        data_request.request_details = payload.request_details

    data_request.updated_at = models.utc_now()
    db.commit()
    db.expire_all()
    return _get_data_request_or_404(db, request_id)


@router.post("/data-requests/{request_id}/notes", response_model=DataRequestNoteResponse, status_code=201)
def add_data_request_note(
    request_id: UUID,
    payload: DataRequestNoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.DataRequestNote:
    require_data_request_access(db, current_user, request_id)
    data_request = _get_data_request_or_404(db, request_id)
    note = models.DataRequestNote(
        data_request_id=data_request.id,
        note=payload.note,
        created_by=payload.created_by,
    )
    db.add(note)
    db.flush()
    _add_audit_event(
        db,
        data_request.id,
        "note_added",
        "Note added.",
        {"created_by": payload.created_by},
    )
    data_request.updated_at = models.utc_now()
    db.commit()
    db.refresh(note)
    return note
