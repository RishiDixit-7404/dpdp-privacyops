from __future__ import annotations

from collections import Counter, defaultdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import models
from app.schemas import (
    EvidenceReportDataCategory,
    EvidenceReportProject,
    EvidenceReportReadiness,
    EvidenceReportResponse,
    EvidenceReportSystem,
    EvidenceReportTopRisk,
    RiskLevel,
    SourceType,
)


TRUST_POSITIONING = (
    "We do not want your raw personal data. The scanner runs inside your environment and sends only metadata, "
    "masked examples, confidence scores, and risk tags."
)
RISK_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def build_evidence_report(db: Session, project_id: UUID) -> EvidenceReportResponse | None:
    project = db.scalar(
        select(models.Project)
        .where(models.Project.id == project_id)
        .options(joinedload(models.Project.organization))
    )
    if project is None:
        return None

    findings = list(
        db.scalars(
            select(models.Finding)
            .join(models.Scan)
            .where(models.Scan.project_id == project_id)
        ).all()
    )
    data_requests = list(
        db.scalars(select(models.DataRequest).where(models.DataRequest.project_id == project_id)).all()
    )
    consent_events = list(
        db.scalars(select(models.ConsentEvent).where(models.ConsentEvent.project_id == project_id)).all()
    )

    return EvidenceReportResponse(
        project=EvidenceReportProject(
            id=project.id,
            name=project.name,
            organization_name=project.organization.name,
        ),
        generated_at=models.utc_now(),
        trust_positioning=TRUST_POSITIONING,
        evidence_scope="Technical readiness evidence generated from local scanner metadata, DSR workflow records, and consent event logs.",
        systems_scanned=_systems_scanned(findings),
        data_categories=_data_categories(findings),
        top_risks=_top_risks(findings),
        dsr_readiness=_dsr_readiness(data_requests),
        consent_readiness=_consent_readiness(consent_events),
        remediation_gaps=_remediation_gaps(findings, data_requests, consent_events),
        technical_evidence_language="This report summarizes implementation evidence and operational gaps for DPDP readiness discussions.",
        legal_certification_disclaimer="This is not legal certification and should not be presented as a compliance certificate.",
    )


def _systems_scanned(findings: list[models.Finding]) -> list[EvidenceReportSystem]:
    totals: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"finding_count": 0, "high_or_critical_count": 0})
    for finding in findings:
        key = (finding.source_name, finding.source_type)
        totals[key]["finding_count"] += 1
        if finding.risk_level in {"high", "critical"}:
            totals[key]["high_or_critical_count"] += 1

    return [
        EvidenceReportSystem(
            name=source_name,
            source_type=SourceType(source_type),
            finding_count=counts["finding_count"],
            high_or_critical_count=counts["high_or_critical_count"],
        )
        for (source_name, source_type), counts in sorted(totals.items())
    ]


def _data_categories(findings: list[models.Finding]) -> list[EvidenceReportDataCategory]:
    counts = Counter(finding.pii_type for finding in findings)
    highest: dict[str, str] = {}
    for finding in findings:
        current = highest.get(finding.pii_type)
        if current is None or RISK_ORDER[finding.risk_level] > RISK_ORDER[current]:
            highest[finding.pii_type] = finding.risk_level

    return [
        EvidenceReportDataCategory(
            pii_type=pii_type,
            finding_count=counts[pii_type],
            highest_risk_level=RiskLevel(highest[pii_type]),
        )
        for pii_type in sorted(counts)
    ]


def _top_risks(findings: list[models.Finding]) -> list[EvidenceReportTopRisk]:
    sorted_findings = sorted(
        findings,
        key=lambda finding: (RISK_ORDER[finding.risk_level], finding.confidence_score),
        reverse=True,
    )
    return [
        EvidenceReportTopRisk(
            source_name=finding.source_name,
            table_or_file=finding.table_or_file,
            field_name=finding.field_name,
            pii_type=finding.pii_type,
            risk_level=RiskLevel(finding.risk_level),
            confidence_score=finding.confidence_score,
            masked_examples=finding.masked_examples,
            suggested_action=finding.suggested_action,
        )
        for finding in sorted_findings[:6]
    ]


def _dsr_readiness(data_requests: list[models.DataRequest]) -> EvidenceReportReadiness:
    counts = Counter(request.request_type for request in data_requests)
    metrics = {
        "total_requests": len(data_requests),
        "access_requests": counts.get("access", 0),
        "deletion_requests": counts.get("deletion", 0),
        "grievance_requests": counts.get("grievance", 0),
    }
    if data_requests:
        return EvidenceReportReadiness(
            status="demo_ready",
            summary="DSR inbox has workflow records for privacy request handling evidence.",
            metrics=metrics,
        )
    return EvidenceReportReadiness(
        status="needs_demo_data",
        summary="No User Data Requests exist yet for this project.",
        metrics=metrics,
    )


def _consent_readiness(consent_events: list[models.ConsentEvent]) -> EvidenceReportReadiness:
    counts = Counter(event.status for event in consent_events)
    purpose_count = len({event.purpose for event in consent_events})
    metrics = {
        "total_events": len(consent_events),
        "granted_events": counts.get("granted", 0),
        "withdrawn_events": counts.get("withdrawn", 0),
        "purpose_count": purpose_count,
    }
    if consent_events:
        return EvidenceReportReadiness(
            status="demo_ready",
            summary="Consent ledger has append-only granted/withdrawn events by purpose.",
            metrics=metrics,
        )
    return EvidenceReportReadiness(
        status="needs_demo_data",
        summary="No consent events exist yet for this project.",
        metrics=metrics,
    )


def _remediation_gaps(
    findings: list[models.Finding],
    data_requests: list[models.DataRequest],
    consent_events: list[models.ConsentEvent],
) -> list[str]:
    gaps: list[str] = []
    if any(finding.risk_level in {"high", "critical"} for finding in findings):
        gaps.append("Prioritize redaction and access controls for high and critical scanner findings.")
    if any("ticket" in finding.table_or_file or "logs" in finding.table_or_file for finding in findings):
        gaps.append("Add evidence of log and support-ticket minimization before broad production rollout.")
    if any("ai_tutor" in finding.table_or_file or "prompt" in finding.field_name for finding in findings):
        gaps.append("Document prompt ingestion controls for student data before AI workflow expansion.")
    if not data_requests:
        gaps.append("Seed or create DSR workflow records to prove request handling readiness.")
    if not consent_events:
        gaps.append("Record consent events for key purposes to prove consent ledger readiness.")
    return gaps or ["No immediate demo remediation gaps detected from current metadata."]
