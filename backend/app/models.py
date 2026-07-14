from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


SCAN_TYPES = ("csv", "postgres", "json")
SOURCE_TYPES = ("csv", "postgres", "json")
RISK_LEVELS = ("low", "medium", "high", "critical")
DETECTION_METHODS = ("column_name", "regex_value", "combined")
DATA_REQUEST_TYPES = ("access", "correction", "deletion", "consent_withdrawal", "grievance")
DATA_REQUEST_STATUSES = ("new", "verifying", "in_progress", "completed", "rejected")
DATA_REQUEST_AUDIT_EVENT_TYPES = (
    "created",
    "status_changed",
    "note_added",
    "assigned",
    "due_date_changed",
    "completed",
    "rejected",
)
CONSENT_STATUSES = ("granted", "withdrawn")
READINESS_SCAN_CUSTOMER_SEGMENTS = ("edtech", "healthtech", "hrtech", "ai_saas", "b2b_saas", "other")
READINESS_SCAN_STATUSES = (
    "draft",
    "inputs_requested",
    "inputs_received",
    "scanning",
    "report_ready",
    "walkthrough_done",
    "converted_to_subscription",
    "closed_lost",
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    projects: Mapped[list[Project]] = relationship(back_populates="organization", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    organization: Mapped[Organization] = relationship(back_populates="projects")
    scans: Mapped[list[Scan]] = relationship(back_populates="project", cascade="all, delete-orphan")
    data_requests: Mapped[list[DataRequest]] = relationship(back_populates="project", cascade="all, delete-orphan")
    consent_events: Mapped[list[ConsentEvent]] = relationship(back_populates="project", cascade="all, delete-orphan")
    readiness_scans: Mapped[list[ReadinessScan]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"
    __table_args__ = (
        CheckConstraint("scan_type in ('csv', 'postgres', 'json')", name="ck_scans_scan_type"),
        CheckConstraint("raw_pii_uploaded = false", name="ck_scans_raw_pii_uploaded_false"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scanner_scan_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    scanner_version: Mapped[str] = mapped_column(String(64), nullable=False)
    scan_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source: Mapped[str] = mapped_column(String(512), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_pii_uploaded: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    project: Mapped[Project] = relationship(back_populates="scans")
    findings: Mapped[list[Finding]] = relationship(back_populates="scan", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"
    __table_args__ = (
        UniqueConstraint("scan_id", "scanner_finding_id", name="uq_findings_scan_scanner_finding_id"),
        CheckConstraint("source_type in ('csv', 'postgres', 'json')", name="ck_findings_source_type"),
        CheckConstraint("confidence_score >= 0 and confidence_score <= 1", name="ck_findings_confidence_score"),
        CheckConstraint("risk_level in ('low', 'medium', 'high', 'critical')", name="ck_findings_risk_level"),
        CheckConstraint(
            "detection_method in ('column_name', 'regex_value', 'combined')",
            name="ck_findings_detection_method",
        ),
        CheckConstraint("sample_count >= 0", name="ck_findings_sample_count"),
        CheckConstraint("match_count >= 0", name="ck_findings_match_count"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    scan_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scanner_finding_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_name: Mapped[str] = mapped_column(String(512), nullable=False)
    table_or_file: Mapped[str] = mapped_column(String(512), nullable=False)
    field_name: Mapped[str] = mapped_column(String(512), nullable=False)
    pii_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    detection_method: Mapped[str] = mapped_column(String(32), nullable=False)
    masked_examples: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False)
    match_count: Mapped[int] = mapped_column(Integer, nullable=False)
    suggested_action: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    scan: Mapped[Scan] = relationship(back_populates="findings")


class DataRequest(Base):
    __tablename__ = "data_requests"
    __table_args__ = (
        CheckConstraint(
            "request_type in ('access', 'correction', 'deletion', 'consent_withdrawal', 'grievance')",
            name="ck_data_requests_request_type",
        ),
        CheckConstraint(
            "status in ('new', 'verifying', 'in_progress', 'completed', 'rejected')",
            name="ck_data_requests_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    request_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="new", index=True)
    requester_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requester_email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    requester_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    request_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[Project] = relationship(back_populates="data_requests")
    notes: Mapped[list[DataRequestNote]] = relationship(
        back_populates="data_request",
        cascade="all, delete-orphan",
        order_by="DataRequestNote.created_at",
    )
    audit_events: Mapped[list[DataRequestAuditEvent]] = relationship(
        back_populates="data_request",
        cascade="all, delete-orphan",
        order_by="DataRequestAuditEvent.created_at",
    )


class DataRequestNote(Base):
    __tablename__ = "data_request_notes"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    data_request_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("data_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    data_request: Mapped[DataRequest] = relationship(back_populates="notes")


class DataRequestAuditEvent(Base):
    __tablename__ = "data_request_audit_events"
    __table_args__ = (
        CheckConstraint(
            "event_type in ('created', 'status_changed', 'note_added', 'assigned', 'due_date_changed', 'completed', 'rejected')",
            name="ck_data_request_audit_events_event_type",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    data_request_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("data_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_metadata: Mapped[dict[str, object] | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    data_request: Mapped[DataRequest] = relationship(back_populates="audit_events")


class ConsentEvent(Base):
    __tablename__ = "consent_events"
    __table_args__ = (
        CheckConstraint("status in ('granted', 'withdrawn')", name="ck_consent_events_status"),
        CheckConstraint("length(trim(external_user_id)) > 0", name="ck_consent_events_external_user_id_not_empty"),
        CheckConstraint("length(trim(purpose)) > 0", name="ck_consent_events_purpose_not_empty"),
        CheckConstraint("length(trim(notice_version)) > 0", name="ck_consent_events_notice_version_not_empty"),
        Index(
            "ix_consent_events_project_user_purpose_occurred",
            "project_id",
            "external_user_id",
            "purpose",
            "occurred_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    external_user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    purpose: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    notice_version: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    event_metadata: Mapped[dict[str, object] | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    project: Mapped[Project] = relationship(back_populates="consent_events")


def readiness_scan_checklist_defaults() -> dict[str, bool]:
    return {
        "schema_dump": False,
        "masked_csv_exports": False,
        "log_samples": False,
        "privacy_notice": False,
        "third_party_tools": False,
        "ai_prompt_samples": False,
    }


class ReadinessScan(Base):
    __tablename__ = "readiness_scans"
    __table_args__ = (
        CheckConstraint(
            "customer_segment in ('edtech', 'healthtech', 'hrtech', 'ai_saas', 'b2b_saas', 'other')",
            name="ck_readiness_scans_customer_segment",
        ),
        CheckConstraint(
            "status in ('draft', 'inputs_requested', 'inputs_received', 'scanning', 'report_ready', "
            "'walkthrough_done', 'converted_to_subscription', 'closed_lost')",
            name="ck_readiness_scans_status",
        ),
        CheckConstraint("price_inr >= 0", name="ck_readiness_scans_price_inr"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_segment: Mapped[str] = mapped_column(String(32), nullable=False)
    package_name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="draft", index=True)
    input_checklist: Mapped[dict[str, bool]] = mapped_column(JSON, nullable=False, default=readiness_scan_checklist_defaults)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    project: Mapped[Project] = relationship(back_populates="readiness_scans")
