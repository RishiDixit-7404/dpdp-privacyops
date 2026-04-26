from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import models
from app.schemas import (
    EvidenceReportResponse,
    ReportConsentPurposeSummary,
    ReportConsentSummary,
    ReportDataInventorySummary,
    ReportDsrSummary,
    ReportProjectSummary,
    ReportReadinessGap,
    ReportRemediationAction,
    ReportRemediationSummary,
    ReportRiskSummary,
    ReportScanSummary,
    ReportTopRisk,
)


REPORT_VERSION = "0.1.0"
REPORT_DISCLAIMER = (
    "This report is technical evidence of discovered data flows, risks, and workflow status. "
    "It is not a legal compliance certificate."
)
RISK_LEVELS = ("critical", "high", "medium", "low")
RISK_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}
DSR_STATUSES = ("new", "verifying", "in_progress", "completed", "rejected")
OPEN_DSR_STATUSES = {"new", "verifying", "in_progress"}
CLOSED_DSR_STATUSES = {"completed", "rejected"}
FREE_TEXT_FIELD_MARKERS = {
    "message",
    "notes",
    "description",
    "payload",
    "prompt",
    "response",
    "log",
    "logs",
    "metadata",
    "comment",
    "ticket_body",
    "input_text",
    "output_text",
    "request_body",
    "response_body",
}


def build_evidence_report(db: Session, project_id: UUID) -> EvidenceReportResponse | None:
    project = db.scalar(
        select(models.Project)
        .where(models.Project.id == project_id)
        .options(joinedload(models.Project.organization))
    )
    if project is None:
        return None

    generated_at = models.utc_now()
    scans = _load_scans(db, project_id)
    findings = _load_findings(db, project_id)
    data_requests = _load_data_requests(db, project_id)
    consent_events = _load_consent_events(db, project_id)

    scan_summary = _build_scan_summary(scans)
    risk_summary = _build_risk_summary(findings)
    data_inventory_summary = _build_data_inventory_summary(scans, findings, scan_summary.latest_scan_generated_at)
    top_risks = _build_top_risks(findings)
    dsr_summary = _build_dsr_summary(data_requests, generated_at)
    consent_summary = _build_consent_summary(consent_events)
    remediation_summary = _build_remediation_summary(findings)
    readiness_gaps = _build_readiness_gaps(scans, findings, data_requests, dsr_summary, consent_events)

    return EvidenceReportResponse(
        project=ReportProjectSummary(
            id=project.id,
            name=project.name,
            description=project.description,
            organization_name=project.organization.name,
            created_at=project.created_at,
        ),
        generated_at=generated_at,
        report_version=REPORT_VERSION,
        disclaimer=REPORT_DISCLAIMER,
        executive_summary=_build_executive_summary(scan_summary, risk_summary, dsr_summary, consent_summary),
        scan_summary=scan_summary,
        risk_summary=risk_summary,
        data_inventory_summary=data_inventory_summary,
        top_risks=top_risks,
        dsr_summary=dsr_summary,
        consent_summary=consent_summary,
        remediation_summary=remediation_summary,
        readiness_gaps=readiness_gaps,
    )


def _load_scans(db: Session, project_id: UUID) -> list[models.Scan]:
    return list(
        db.scalars(
            select(models.Scan)
            .where(models.Scan.project_id == project_id)
            .order_by(models.Scan.generated_at.desc(), models.Scan.created_at.desc())
        ).all()
    )


def _load_findings(db: Session, project_id: UUID) -> list[models.Finding]:
    return list(
        db.scalars(
            select(models.Finding)
            .join(models.Scan)
            .where(models.Scan.project_id == project_id)
            .order_by(models.Finding.created_at.desc())
        ).all()
    )


def _load_data_requests(db: Session, project_id: UUID) -> list[models.DataRequest]:
    return list(
        db.scalars(
            select(models.DataRequest)
            .where(models.DataRequest.project_id == project_id)
            .order_by(models.DataRequest.created_at.desc())
        ).all()
    )


def _load_consent_events(db: Session, project_id: UUID) -> list[models.ConsentEvent]:
    return list(
        db.scalars(
            select(models.ConsentEvent)
            .where(models.ConsentEvent.project_id == project_id)
            .order_by(models.ConsentEvent.occurred_at.desc(), models.ConsentEvent.created_at.desc())
        ).all()
    )


def _build_scan_summary(scans: list[models.Scan]) -> ReportScanSummary:
    latest_scan = scans[0] if scans else None
    return ReportScanSummary(
        scan_count=len(scans),
        latest_scan_id=latest_scan.id if latest_scan else None,
        latest_scan_source=latest_scan.source if latest_scan else None,
        latest_scan_type=latest_scan.scan_type if latest_scan else None,
        latest_scan_generated_at=latest_scan.generated_at if latest_scan else None,
    )


def _build_risk_summary(findings: list[models.Finding]) -> ReportRiskSummary:
    risk_counts = Counter(finding.risk_level for finding in findings)
    counts_by_risk_level = {risk: risk_counts.get(risk, 0) for risk in RISK_LEVELS}
    highest = next((risk for risk in RISK_LEVELS if counts_by_risk_level[risk] > 0), None)
    return ReportRiskSummary(
        total_findings=len(findings),
        counts_by_risk_level=counts_by_risk_level,
        critical_count=counts_by_risk_level["critical"],
        high_count=counts_by_risk_level["high"],
        highest_risk_level=highest,
    )


def _build_data_inventory_summary(
    scans: list[models.Scan],
    findings: list[models.Finding],
    latest_scan_generated_at: datetime | None,
) -> ReportDataInventorySummary:
    return ReportDataInventorySummary(
        counts_by_pii_type=dict(sorted(Counter(finding.pii_type for finding in findings).items())),
        counts_by_source_type=dict(sorted(Counter(finding.source_type for finding in findings).items())),
        sources_scanned=sorted({scan.source for scan in scans}),
        scan_types=sorted({scan.scan_type for scan in scans}),
        latest_scan_generated_at=latest_scan_generated_at,
    )


def _build_top_risks(findings: list[models.Finding]) -> list[ReportTopRisk]:
    sorted_findings = sorted(
        findings,
        key=lambda finding: (
            RISK_RANK.get(finding.risk_level, 0),
            finding.confidence_score,
            _ensure_aware(finding.created_at),
        ),
        reverse=True,
    )
    return [
        ReportTopRisk(
            risk_level=finding.risk_level,
            pii_type=finding.pii_type,
            source_type=finding.source_type,
            source_name=finding.source_name,
            field_name=finding.field_name,
            confidence_score=finding.confidence_score,
            masked_examples=finding.masked_examples[:3],
            suggested_action=finding.suggested_action,
        )
        for finding in sorted_findings[:10]
    ]


def _build_dsr_summary(data_requests: list[models.DataRequest], now: datetime) -> ReportDsrSummary:
    status_counts = Counter(request.status for request in data_requests)
    type_counts = Counter(request.request_type for request in data_requests)
    open_requests = sum(status_counts.get(status, 0) for status in OPEN_DSR_STATUSES)
    overdue_requests = sum(
        1
        for request in data_requests
        if request.due_date is not None
        and _ensure_aware(request.due_date) < now
        and request.status not in CLOSED_DSR_STATUSES
    )
    latest_request = data_requests[0] if data_requests else None
    return ReportDsrSummary(
        total_requests=len(data_requests),
        counts_by_status={status: status_counts.get(status, 0) for status in DSR_STATUSES},
        counts_by_type=dict(sorted(type_counts.items())),
        open_requests=open_requests,
        overdue_requests=overdue_requests,
        latest_request_created_at=latest_request.created_at if latest_request else None,
    )


def _build_consent_summary(consent_events: list[models.ConsentEvent]) -> ReportConsentSummary:
    status_counts = Counter(event.status for event in consent_events)
    purpose_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"granted": 0, "withdrawn": 0})
    latest_by_purpose: dict[str, datetime] = {}
    for event in consent_events:
        purpose_counts[event.purpose][event.status] += 1
        latest = latest_by_purpose.get(event.purpose)
        if latest is None or _ensure_aware(event.occurred_at) > _ensure_aware(latest):
            latest_by_purpose[event.purpose] = event.occurred_at

    return ReportConsentSummary(
        total_events=len(consent_events),
        granted_count=status_counts.get("granted", 0),
        withdrawn_count=status_counts.get("withdrawn", 0),
        purposes=[
            ReportConsentPurposeSummary(
                purpose=purpose,
                granted_count=counts["granted"],
                withdrawn_count=counts["withdrawn"],
                latest_event_at=latest_by_purpose.get(purpose),
            )
            for purpose, counts in sorted(purpose_counts.items())
        ],
        latest_event_at=consent_events[0].occurred_at if consent_events else None,
    )


def _build_remediation_summary(findings: list[models.Finding]) -> ReportRemediationSummary:
    grouped: dict[str, list[models.Finding]] = defaultdict(list)
    for finding in findings:
        primary_title = _action_title_for_finding(finding)
        grouped[primary_title].append(finding)
        if _is_free_text_field(finding.field_name.lower()) and primary_title != "Redact personal data before log or prompt ingestion":
            grouped["Redact personal data before log or prompt ingestion"].append(finding)

    actions = []
    for title, group in grouped.items():
        highest_risk = max(group, key=lambda finding: RISK_RANK.get(finding.risk_level, 0)).risk_level
        actions.append(
            ReportRemediationAction(
                priority=highest_risk,
                title=title,
                description=_action_description(title),
                affected_fields_count=len({(finding.source_name, finding.field_name) for finding in group}),
                related_pii_types=sorted({finding.pii_type for finding in group}),
                related_sources=sorted({finding.source_name for finding in group}),
            )
        )

    actions.sort(key=lambda action: (RISK_RANK.get(action.priority, 0), action.affected_fields_count), reverse=True)
    return ReportRemediationSummary(
        total_recommended_actions=len(actions),
        critical_actions=sum(1 for action in actions if action.priority == "critical"),
        high_priority_actions=sum(1 for action in actions if action.priority == "high"),
        actions=actions,
    )


def _build_readiness_gaps(
    scans: list[models.Scan],
    findings: list[models.Finding],
    data_requests: list[models.DataRequest],
    dsr_summary: ReportDsrSummary,
    consent_events: list[models.ConsentEvent],
) -> list[ReportReadinessGap]:
    gaps: list[ReportReadinessGap] = []
    risk_counts = Counter(finding.risk_level for finding in findings)
    pii_types = {finding.pii_type for finding in findings}

    if not scans:
        gaps.append(
            ReportReadinessGap(
                severity="medium",
                area="data_discovery",
                message="No scanner uploads exist for this project.",
                suggested_next_step="Run the local scanner against CSV, JSON/JSONL, or Postgres metadata and upload the JSON output.",
            )
        )
    if risk_counts.get("critical", 0) > 0:
        gaps.append(
            ReportReadinessGap(
                severity="critical",
                area="data_discovery",
                message=f"{risk_counts['critical']} critical personal-data findings require review.",
                suggested_next_step="Prioritize critical findings and record remediation ownership before expanding scans.",
            )
        )
    if risk_counts.get("high", 0) > 0:
        gaps.append(
            ReportReadinessGap(
                severity="high",
                area="retention",
                message=f"{risk_counts['high']} high-risk findings need retention and access-control review.",
                suggested_next_step="Confirm purpose limitation, access controls, and deletion workflow coverage for high-risk fields.",
            )
        )
    if not data_requests:
        gaps.append(
            ReportReadinessGap(
                severity="medium",
                area="dsr",
                message="No User Data Request workflow activity has been recorded.",
                suggested_next_step="Create a sample User Data Request workflow and document operating ownership.",
            )
        )
    if dsr_summary.open_requests > 0:
        gaps.append(
            ReportReadinessGap(
                severity="medium",
                area="dsr",
                message=f"{dsr_summary.open_requests} User Data Requests are still open.",
                suggested_next_step="Review open requests and move them through verification, processing, and closure.",
            )
        )
    if dsr_summary.overdue_requests > 0:
        gaps.append(
            ReportReadinessGap(
                severity="high",
                area="dsr",
                message=f"{dsr_summary.overdue_requests} User Data Requests are overdue.",
                suggested_next_step="Resolve overdue requests or document rejection/completion decisions with notes.",
            )
        )
    if not consent_events:
        gaps.append(
            ReportReadinessGap(
                severity="medium",
                area="consent",
                message="No consent events have been recorded.",
                suggested_next_step="Record granted/withdrawn events for key purposes such as marketing, analytics, support, or AI processing.",
            )
        )
    if any(finding.pii_type == "free_text_possible_pii" or _is_free_text_field(finding.field_name.lower()) for finding in findings):
        gaps.append(
            ReportReadinessGap(
                severity="high",
                area="ai_or_logs",
                message="Possible personal data was found in logs, prompts, support text, or other free-text fields.",
                suggested_next_step="Add redaction before log, support-ticket, analytics, and prompt ingestion.",
            )
        )
    if "authentication_secret" in pii_types:
        gaps.append(
            ReportReadinessGap(
                severity="critical",
                area="security",
                message="Authentication secrets were detected in scanned data.",
                suggested_next_step="Remove the secrets, rotate affected credentials, and prevent future secret logging.",
            )
        )
    if "student_or_child_data" in pii_types:
        gaps.append(
            ReportReadinessGap(
                severity="high",
                area="retention",
                message="Student or child data was found.",
                suggested_next_step="Review access, retention, and purpose limitation for student or child data flows.",
            )
        )
    if "health_data" in pii_types:
        gaps.append(
            ReportReadinessGap(
                severity="high",
                area="retention",
                message="Health data was found.",
                suggested_next_step="Restrict access and review retention for health data flows.",
            )
        )
    return gaps


def _build_executive_summary(
    scan_summary: ReportScanSummary,
    risk_summary: ReportRiskSummary,
    dsr_summary: ReportDsrSummary,
    consent_summary: ReportConsentSummary,
) -> str:
    return (
        "This technical evidence report summarizes "
        f"{scan_summary.scan_count} scans, "
        f"{risk_summary.total_findings} personal-data findings, "
        f"{risk_summary.critical_count} critical risks, "
        f"{risk_summary.high_count} high risks, "
        f"{dsr_summary.open_requests} open user data requests, and "
        f"{consent_summary.total_events} consent events for this project."
    )


def _action_title_for_finding(finding: models.Finding) -> str:
    field_name = finding.field_name.lower()
    if finding.pii_type in {"aadhaar", "pan"}:
        return "Review Aadhaar/PAN storage and retention"
    if finding.pii_type == "authentication_secret":
        return "Remove and rotate exposed authentication secrets"
    if finding.pii_type in {"email", "indian_phone", "upi_id"}:
        return "Add deletion workflow coverage for contact data"
    if finding.pii_type in {"health_data", "student_or_child_data"}:
        return "Restrict access to health or student data"
    if finding.pii_type == "free_text_possible_pii" or _is_free_text_field(field_name):
        return "Redact personal data before log or prompt ingestion"
    return finding.suggested_action[:120]


def _action_description(title: str) -> str:
    descriptions = {
        "Review Aadhaar/PAN storage and retention": "Confirm strict purpose, encryption/tokenization, access controls, and retention limits for high-risk identifiers.",
        "Remove and rotate exposed authentication secrets": "Remove secrets from files, logs, or metadata immediately and rotate affected keys or tokens.",
        "Add deletion workflow coverage for contact data": "Ensure contact identifiers are mapped to user deletion and access workflows with retention rules.",
        "Restrict access to health or student data": "Apply tighter access controls, review retention, and limit processing to the stated purpose.",
        "Redact personal data before log or prompt ingestion": "Add redaction before log, support-ticket, analytics, or AI prompt ingestion.",
    }
    return descriptions.get(title, title)


def _is_free_text_field(field_name: str) -> bool:
    tokens = field_name.replace("[]", "").replace(".", "_").split("_")
    return any(marker in tokens or marker in field_name for marker in FREE_TEXT_FIELD_MARKERS)


def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value
