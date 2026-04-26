from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.schemas import ScanSummary, ScannerUpload


RISK_LEVEL_ORDER = ("critical", "high", "medium", "low")


class DuplicateScannerScanError(Exception):
    """Raised when a scanner scan_id was already ingested."""


@dataclass(frozen=True)
class IngestionResult:
    scan: models.Scan
    summary: ScanSummary


def ingest_scanner_upload(db: Session, project_id: UUID, payload: ScannerUpload) -> IngestionResult:
    existing_scan = db.scalar(select(models.Scan).where(models.Scan.scanner_scan_id == payload.scan_id))
    if existing_scan is not None:
        raise DuplicateScannerScanError(payload.scan_id)

    if payload.raw_pii_uploaded is not False:
        raise ValueError("raw_pii_uploaded must be false")

    scan = models.Scan(
        project_id=project_id,
        scanner_scan_id=payload.scan_id,
        scanner_version=payload.scanner_version,
        scan_type=payload.scan_type.value,
        source=payload.source,
        generated_at=payload.generated_at,
        raw_pii_uploaded=False,
    )
    db.add(scan)
    db.flush()

    for finding in payload.findings:
        db.add(
            models.Finding(
                scan_id=scan.id,
                scanner_finding_id=finding.finding_id,
                source_type=finding.source_type.value,
                source_name=finding.source_name,
                table_or_file=finding.table_or_file,
                field_name=finding.field_name,
                pii_type=finding.pii_type,
                confidence_score=finding.confidence_score,
                risk_level=finding.risk_level.value,
                detection_method=finding.detection_method.value,
                masked_examples=finding.masked_examples,
                sample_count=finding.sample_count,
                match_count=finding.match_count,
                suggested_action=finding.suggested_action,
            )
        )

    summary = summarize_upload(payload)
    db.commit()
    db.refresh(scan)
    return IngestionResult(scan=scan, summary=summary)


def summarize_upload(payload: ScannerUpload) -> ScanSummary:
    risk_counts = Counter(finding.risk_level.value for finding in payload.findings)
    pii_counts = Counter(finding.pii_type for finding in payload.findings)
    return _summary_from_counts(total_findings=len(payload.findings), risk_counts=risk_counts, pii_counts=pii_counts)


def summarize_scan(scan: models.Scan) -> ScanSummary:
    risk_counts = Counter(finding.risk_level for finding in scan.findings)
    pii_counts = Counter(finding.pii_type for finding in scan.findings)
    return _summary_from_counts(total_findings=len(scan.findings), risk_counts=risk_counts, pii_counts=pii_counts)


def _summary_from_counts(
    total_findings: int,
    risk_counts: Counter[str],
    pii_counts: Counter[str],
) -> ScanSummary:
    return ScanSummary(
        total_findings=total_findings,
        counts_by_risk_level={risk_level: risk_counts.get(risk_level, 0) for risk_level in RISK_LEVEL_ORDER},
        counts_by_pii_type=dict(pii_counts),
        critical_count=risk_counts.get("critical", 0),
        high_count=risk_counts.get("high", 0),
    )
