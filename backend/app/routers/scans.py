from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.deps import get_db
from app.schemas import ScanDetailResponse, ScannerUpload, ScanResponse, ScanUploadResponse
from app.services.scan_ingestion import DuplicateScannerScanError, ingest_scanner_upload, summarize_scan


router = APIRouter(tags=["scans"])


@router.post("/projects/{project_id}/scans/upload", response_model=ScanUploadResponse, status_code=201)
def upload_scan(project_id: UUID, payload: ScannerUpload, db: Session = Depends(get_db)) -> ScanUploadResponse:
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = ingest_scanner_upload(db, project_id, payload)
    except DuplicateScannerScanError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="scanner_scan_id already ingested") from exc

    response = ScanResponse.model_validate(result.scan)
    return ScanUploadResponse(**response.model_dump(), summary=result.summary)


@router.get("/projects/{project_id}/scans", response_model=list[ScanResponse])
def list_project_scans(project_id: UUID, db: Session = Depends(get_db)) -> list[models.Scan]:
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    statement = select(models.Scan).where(models.Scan.project_id == project_id).order_by(models.Scan.created_at.desc())
    return list(db.scalars(statement).all())


@router.get("/scans/{scan_id}", response_model=ScanDetailResponse)
def get_scan(scan_id: UUID, db: Session = Depends(get_db)) -> ScanDetailResponse:
    scan = db.scalar(
        select(models.Scan)
        .where(models.Scan.id == scan_id)
        .options(selectinload(models.Scan.findings))
    )
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    response = ScanResponse.model_validate(scan)
    return ScanDetailResponse(**response.model_dump(), summary=summarize_scan(scan))

