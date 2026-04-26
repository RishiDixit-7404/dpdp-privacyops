from __future__ import annotations

from datetime import datetime
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
