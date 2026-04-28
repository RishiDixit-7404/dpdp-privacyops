from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.deps import get_current_user, get_db
from app.schemas import EvidenceReportResponse
from app.services.access_control import require_project_access
from app.services.evidence_report import build_evidence_report


router = APIRouter(tags=["reports"])


@router.get("/projects/{project_id}/evidence-report", response_model=EvidenceReportResponse)
def get_evidence_report(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> EvidenceReportResponse:
    require_project_access(db, current_user, project_id)
    report = build_evidence_report(db, project_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return report
