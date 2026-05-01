from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app import models
from app.deps import get_db
from app.schemas import (
    ReadinessScanChecklist,
    ReadinessScanChecklistUpdate,
    ReadinessScanCreate,
    ReadinessScanProjectSummary,
    ReadinessScanResponse,
    ReadinessScanStatus,
    ReadinessScanSummaryResponse,
    ReadinessScanUpdate,
)


router = APIRouter(prefix="/api/readiness-scans", tags=["readiness scans"])
CHECKLIST_KEYS = tuple(models.readiness_scan_checklist_defaults().keys())


def _get_project_or_404(db: Session, project_id: UUID) -> models.Project:
    project = db.scalar(
        select(models.Project)
        .where(models.Project.id == project_id)
        .options(joinedload(models.Project.organization))
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_readiness_scan_or_404(db: Session, scan_id: UUID) -> models.ReadinessScan:
    readiness_scan = db.scalar(
        select(models.ReadinessScan)
        .where(models.ReadinessScan.id == scan_id)
        .options(joinedload(models.ReadinessScan.project).joinedload(models.Project.organization))
    )
    if readiness_scan is None:
        raise HTTPException(status_code=404, detail="Readiness scan not found")
    return readiness_scan


def _normalized_checklist(value: dict[str, object] | None) -> dict[str, bool]:
    checklist = models.readiness_scan_checklist_defaults()
    if value:
        for key in CHECKLIST_KEYS:
            checklist[key] = bool(value.get(key, False))
    return checklist


@router.get("", response_model=list[ReadinessScanResponse])
def list_readiness_scans(
    project_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[models.ReadinessScan]:
    filters = []
    if project_id is not None:
        filters.append(models.ReadinessScan.project_id == project_id)
    statement = select(models.ReadinessScan).where(*filters).order_by(models.ReadinessScan.created_at.desc())
    return list(db.scalars(statement).all())


@router.post("", response_model=ReadinessScanResponse, status_code=201)
def create_readiness_scan(payload: ReadinessScanCreate, db: Session = Depends(get_db)) -> models.ReadinessScan:
    _get_project_or_404(db, payload.project_id)
    readiness_scan = models.ReadinessScan(
        project_id=payload.project_id,
        customer_name=payload.customer_name,
        customer_segment=payload.customer_segment.value,
        package_name=payload.package_name,
        price_inr=payload.price_inr,
        status=payload.status.value,
        input_checklist=payload.input_checklist.model_dump(),
        notes=payload.notes,
    )
    db.add(readiness_scan)
    db.commit()
    db.refresh(readiness_scan)
    return readiness_scan


@router.get("/{scan_id}", response_model=ReadinessScanResponse)
def get_readiness_scan(scan_id: UUID, db: Session = Depends(get_db)) -> models.ReadinessScan:
    return _get_readiness_scan_or_404(db, scan_id)


@router.patch("/{scan_id}", response_model=ReadinessScanResponse)
def update_readiness_scan(
    scan_id: UUID,
    payload: ReadinessScanUpdate,
    db: Session = Depends(get_db),
) -> models.ReadinessScan:
    readiness_scan = _get_readiness_scan_or_404(db, scan_id)
    changes = payload.model_dump(exclude_unset=True)

    if payload.customer_name is not None:
        readiness_scan.customer_name = payload.customer_name
    if payload.customer_segment is not None:
        readiness_scan.customer_segment = payload.customer_segment.value
    if payload.package_name is not None:
        readiness_scan.package_name = payload.package_name
    if payload.price_inr is not None:
        readiness_scan.price_inr = payload.price_inr
    if payload.status is not None:
        readiness_scan.status = payload.status.value
    if payload.input_checklist is not None:
        readiness_scan.input_checklist = payload.input_checklist.model_dump()
    if "notes" in changes:
        readiness_scan.notes = payload.notes

    readiness_scan.updated_at = models.utc_now()
    db.commit()
    db.refresh(readiness_scan)
    return readiness_scan


@router.post("/{scan_id}/checklist", response_model=ReadinessScanResponse)
def update_readiness_scan_checklist(
    scan_id: UUID,
    payload: ReadinessScanChecklistUpdate,
    db: Session = Depends(get_db),
) -> models.ReadinessScan:
    readiness_scan = _get_readiness_scan_or_404(db, scan_id)
    checklist = _normalized_checklist(readiness_scan.input_checklist)
    for key, value in payload.model_dump(exclude_unset=True).items():
        checklist[key] = bool(value)
    readiness_scan.input_checklist = checklist
    readiness_scan.updated_at = models.utc_now()
    db.commit()
    db.refresh(readiness_scan)
    return readiness_scan


@router.get("/{scan_id}/summary", response_model=ReadinessScanSummaryResponse)
def get_readiness_scan_summary(scan_id: UUID, db: Session = Depends(get_db)) -> ReadinessScanSummaryResponse:
    readiness_scan = _get_readiness_scan_or_404(db, scan_id)
    project = readiness_scan.project
    checklist = ReadinessScanChecklist.model_validate(_normalized_checklist(readiness_scan.input_checklist))
    checklist_values = checklist.model_dump()
    completed_count = sum(1 for value in checklist_values.values() if value)
    completion_percentage = int(round((completed_count / len(checklist_values)) * 100))

    finding_count = (
        db.scalar(
            select(func.count())
            .select_from(models.Finding)
            .join(models.Scan)
            .where(models.Scan.project_id == readiness_scan.project_id)
        )
        or 0
    )
    high_or_critical_count = (
        db.scalar(
            select(func.count())
            .select_from(models.Finding)
            .join(models.Scan)
            .where(
                models.Scan.project_id == readiness_scan.project_id,
                models.Finding.risk_level.in_(("high", "critical")),
            )
        )
        or 0
    )
    dsr_request_count = (
        db.scalar(
            select(func.count())
            .select_from(models.DataRequest)
            .where(models.DataRequest.project_id == readiness_scan.project_id)
        )
        or 0
    )
    consent_event_count = (
        db.scalar(
            select(func.count())
            .select_from(models.ConsentEvent)
            .where(models.ConsentEvent.project_id == readiness_scan.project_id)
        )
        or 0
    )

    return ReadinessScanSummaryResponse(
        scan_id=readiness_scan.id,
        package_name=readiness_scan.package_name,
        price_inr=readiness_scan.price_inr,
        status=ReadinessScanStatus(readiness_scan.status),
        checklist_completion_percentage=completion_percentage,
        linked_project=ReadinessScanProjectSummary(
            id=project.id,
            name=project.name,
            organization_name=project.organization.name,
        ),
        finding_count=finding_count,
        high_or_critical_risk_count=high_or_critical_count,
        dsr_request_count=dsr_request_count,
        consent_event_count=consent_event_count,
        evidence_report_available=True,
        next_recommended_action=_next_recommended_action(
            ReadinessScanStatus(readiness_scan.status),
            completion_percentage,
            finding_count,
            high_or_critical_count,
        ),
    )


def _next_recommended_action(
    status: ReadinessScanStatus,
    completion_percentage: int,
    finding_count: int,
    high_or_critical_count: int,
) -> str:
    if status in {ReadinessScanStatus.draft, ReadinessScanStatus.inputs_requested}:
        return "Request safe customer inputs"
    if completion_percentage < 100:
        return "Request safe customer inputs"
    if status == ReadinessScanStatus.inputs_received:
        return "Run local scanner"
    if finding_count == 0:
        return "Run local scanner"
    if status == ReadinessScanStatus.report_ready:
        return "Schedule 30-minute walkthrough"
    if status == ReadinessScanStatus.scanning or high_or_critical_count > 0:
        return "Review high-risk findings"
    if status == ReadinessScanStatus.walkthrough_done:
        return "Ask customer to convert to monthly monitoring"
    if status == ReadinessScanStatus.converted_to_subscription:
        return "Move customer into monthly monitoring"
    if status == ReadinessScanStatus.closed_lost:
        return "No action unless customer reopens the scan"
    return "Generate evidence report"
