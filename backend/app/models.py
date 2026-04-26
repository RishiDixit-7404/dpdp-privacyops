from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


SCAN_TYPES = ("csv", "postgres", "json")
SOURCE_TYPES = ("csv", "postgres", "json")
RISK_LEVELS = ("low", "medium", "high", "critical")
DETECTION_METHODS = ("column_name", "regex_value", "combined")


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

