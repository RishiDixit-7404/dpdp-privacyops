from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app import models
from app.deps import get_db
from app.schemas import FindingResponse, RiskLevel, SourceType


router = APIRouter(tags=["findings"])


def _risk_sort_expression():
    return case(
        (models.Finding.risk_level == "critical", 4),
        (models.Finding.risk_level == "high", 3),
        (models.Finding.risk_level == "medium", 2),
        (models.Finding.risk_level == "low", 1),
        else_=0,
    )


@router.get("/projects/{project_id}/findings", response_model=list[FindingResponse])
def list_project_findings(
    project_id: UUID,
    risk_level: RiskLevel | None = Query(default=None),
    pii_type: str | None = Query(default=None),
    source_type: SourceType | None = Query(default=None),
    scan_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[models.Finding]:
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    statement = select(models.Finding).join(models.Scan).where(models.Scan.project_id == project_id)
    if risk_level is not None:
        statement = statement.where(models.Finding.risk_level == risk_level.value)
    if pii_type is not None:
        statement = statement.where(models.Finding.pii_type == pii_type)
    if source_type is not None:
        statement = statement.where(models.Finding.source_type == source_type.value)
    if scan_id is not None:
        statement = statement.where(models.Finding.scan_id == scan_id)

    statement = statement.order_by(_risk_sort_expression().desc(), models.Finding.confidence_score.desc())
    return list(db.scalars(statement).all())


@router.get("/scans/{scan_id}/findings", response_model=list[FindingResponse])
def list_scan_findings(scan_id: UUID, db: Session = Depends(get_db)) -> list[models.Finding]:
    scan = db.get(models.Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    statement = (
        select(models.Finding)
        .where(models.Finding.scan_id == scan_id)
        .order_by(_risk_sort_expression().desc(), models.Finding.confidence_score.desc())
    )
    return list(db.scalars(statement).all())

