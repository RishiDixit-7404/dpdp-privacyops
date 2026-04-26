from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScanType(StrEnum):
    csv = "csv"
    postgres = "postgres"
    json = "json"


class SourceType(StrEnum):
    csv = "csv"
    postgres = "postgres"
    json = "json"


class RiskLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class DetectionMethod(StrEnum):
    column_name = "column_name"
    regex_value = "regex_value"
    combined = "combined"


class DataRequestType(StrEnum):
    access = "access"
    correction = "correction"
    deletion = "deletion"
    consent_withdrawal = "consent_withdrawal"
    grievance = "grievance"


class DataRequestStatus(StrEnum):
    new = "new"
    verifying = "verifying"
    in_progress = "in_progress"
    completed = "completed"
    rejected = "rejected"


class DataRequestAuditEventType(StrEnum):
    created = "created"
    status_changed = "status_changed"
    note_added = "note_added"
    assigned = "assigned"
    due_date_changed = "due_date_changed"
    completed = "completed"
    rejected = "rejected"


class ConsentStatus(StrEnum):
    granted = "granted"
    withdrawn = "withdrawn"


def validate_email_for_mvp(value: str) -> str:
    normalized = value.strip()
    if not normalized or "@" not in normalized:
        raise ValueError("requester_email must be a valid email address")
    local_part, domain = normalized.rsplit("@", 1)
    if not local_part or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise ValueError("requester_email must be a valid email address")
    return normalized


def ensure_timezone_aware(value: datetime | None) -> datetime | None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        return value.replace(tzinfo=timezone.utc)
    return value


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime


class ProjectCreate(BaseModel):
    organization_name: str = Field(min_length=1, max_length=255)
    project_name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    created_at: datetime
    organization: OrganizationResponse


class ScannerFindingUpload(BaseModel):
    finding_id: str = Field(min_length=1)
    source_type: SourceType
    source_name: str
    table_or_file: str
    field_name: str
    pii_type: str = Field(min_length=1)
    confidence_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    detection_method: DetectionMethod
    masked_examples: list[str] = Field(default_factory=list, max_length=3)
    sample_count: int = Field(ge=0)
    match_count: int = Field(ge=0)
    suggested_action: str = Field(min_length=1)


class ScannerUpload(BaseModel):
    scan_id: str = Field(min_length=1)
    scanner_version: str = Field(min_length=1)
    scan_type: ScanType
    source: str = Field(min_length=1)
    generated_at: datetime
    raw_pii_uploaded: Literal[False] = False
    findings: list[ScannerFindingUpload]

    @field_validator("generated_at")
    @classmethod
    def generated_at_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("generated_at must be timezone-aware")
        return value


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scan_id: UUID
    scanner_finding_id: str
    source_type: SourceType
    source_name: str
    table_or_file: str
    field_name: str
    pii_type: str
    confidence_score: float
    risk_level: RiskLevel
    detection_method: DetectionMethod
    masked_examples: list[str]
    sample_count: int
    match_count: int
    suggested_action: str
    created_at: datetime


class ScanSummary(BaseModel):
    total_findings: int
    counts_by_risk_level: dict[str, int]
    counts_by_pii_type: dict[str, int]
    critical_count: int
    high_count: int


class FindingListResponse(BaseModel):
    items: list[FindingResponse]
    total: int
    limit: int
    offset: int


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    scanner_scan_id: str
    scanner_version: str
    scan_type: ScanType
    source: str
    generated_at: datetime
    raw_pii_uploaded: bool
    created_at: datetime


class ScanUploadResponse(ScanResponse):
    summary: ScanSummary


class ScanDetailResponse(ScanResponse):
    summary: ScanSummary


class DataRequestCreate(BaseModel):
    request_type: DataRequestType
    requester_name: str | None = Field(default=None, max_length=255)
    requester_email: str = Field(min_length=3, max_length=320)
    requester_identifier: str | None = Field(default=None, max_length=255)
    request_details: str | None = Field(default=None, max_length=5000)
    due_date: datetime | None = None
    assigned_to: str | None = Field(default=None, max_length=255)

    @field_validator("requester_email")
    @classmethod
    def requester_email_must_look_valid(cls, value: str) -> str:
        return validate_email_for_mvp(value)


class DataRequestUpdate(BaseModel):
    status: DataRequestStatus | None = None
    assigned_to: str | None = Field(default=None, max_length=255)
    due_date: datetime | None = None
    request_details: str | None = Field(default=None, max_length=5000)


class DataRequestNoteCreate(BaseModel):
    note: str = Field(min_length=1, max_length=5000)
    created_by: str | None = Field(default=None, max_length=255)

    @field_validator("note")
    @classmethod
    def note_cannot_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("note cannot be empty")
        return normalized


class DataRequestNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    data_request_id: UUID
    note: str
    created_by: str | None
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def datetimes_must_be_timezone_aware(cls, value: datetime) -> datetime | None:
        return ensure_timezone_aware(value)


class DataRequestAuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    data_request_id: UUID
    event_type: DataRequestAuditEventType
    message: str
    metadata: dict[str, object] | None = Field(default=None, validation_alias="event_metadata")
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def datetimes_must_be_timezone_aware(cls, value: datetime) -> datetime | None:
        return ensure_timezone_aware(value)


class DataRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    request_type: DataRequestType
    status: DataRequestStatus
    requester_name: str | None
    requester_email: str
    requester_identifier: str | None
    request_details: str | None
    due_date: datetime | None
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    @field_validator("due_date", "created_at", "updated_at", "completed_at", mode="before")
    @classmethod
    def datetimes_must_be_timezone_aware(cls, value: datetime | None) -> datetime | None:
        return ensure_timezone_aware(value)


class DataRequestDetailResponse(DataRequestResponse):
    notes: list[DataRequestNoteResponse]
    audit_events: list[DataRequestAuditEventResponse]


class DataRequestListResponse(BaseModel):
    items: list[DataRequestResponse]
    total: int
    limit: int
    offset: int


class PublicDataRequestConfirmation(BaseModel):
    request_id: UUID
    status: Literal["new"]
    message: str


class ConsentEventCreate(BaseModel):
    external_user_id: str = Field(min_length=1, max_length=255)
    purpose: str = Field(min_length=1, max_length=255)
    status: ConsentStatus
    notice_version: str = Field(min_length=1, max_length=64)
    source: str | None = Field(default=None, max_length=255)
    occurred_at: datetime
    metadata: dict[str, object] | None = None

    @field_validator("external_user_id", "purpose", "notice_version")
    @classmethod
    def required_strings_cannot_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("field cannot be empty")
        return normalized

    @field_validator("occurred_at")
    @classmethod
    def occurred_at_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        return value

    @field_validator("metadata")
    @classmethod
    def metadata_must_be_reasonable_size(cls, value: dict[str, object] | None) -> dict[str, object] | None:
        if value is None:
            return value
        encoded = json.dumps(value, separators=(",", ":"), sort_keys=True)
        if len(encoded.encode("utf-8")) > 10 * 1024:
            raise ValueError("metadata must not exceed 10KB")
        return value


class ConsentEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    external_user_id: str
    purpose: str
    status: ConsentStatus
    notice_version: str
    source: str | None
    occurred_at: datetime
    metadata: dict[str, object] | None = Field(default=None, validation_alias="event_metadata")
    created_at: datetime

    @field_validator("occurred_at", "created_at", mode="before")
    @classmethod
    def datetimes_must_be_timezone_aware(cls, value: datetime) -> datetime | None:
        return ensure_timezone_aware(value)


class ConsentEventListResponse(BaseModel):
    items: list[ConsentEventResponse]
    total: int
    limit: int
    offset: int


class ConsentStatusResponse(BaseModel):
    project_id: UUID
    external_user_id: str
    purpose: str
    current_status: ConsentStatus
    notice_version: str
    source: str | None
    occurred_at: datetime
    latest_event_id: UUID

    @field_validator("occurred_at", mode="before")
    @classmethod
    def occurred_at_must_be_timezone_aware(cls, value: datetime) -> datetime | None:
        return ensure_timezone_aware(value)


class ConsentPurposeSummary(BaseModel):
    purpose: str
    granted_count: int
    withdrawn_count: int
    latest_event_at: datetime | None

    @field_validator("latest_event_at", mode="before")
    @classmethod
    def latest_event_at_must_be_timezone_aware(cls, value: datetime | None) -> datetime | None:
        return ensure_timezone_aware(value)


class ConsentSummaryResponse(BaseModel):
    total_events: int
    granted_count: int
    withdrawn_count: int
    purposes: list[ConsentPurposeSummary]
