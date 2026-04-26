from __future__ import annotations

from datetime import datetime
import hashlib
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


PIIType = Literal[
    "email",
    "indian_phone",
    "pan",
    "aadhaar",
    "upi_id",
    "date_of_birth",
    "person_name",
    "address",
    "student_or_child_data",
    "health_data",
    "employment_data",
    "financial_data",
    "authentication_secret",
    "free_text_possible_pii",
]

RiskLevel = Literal["low", "medium", "high", "critical"]
DetectionMethod = Literal["column_name", "regex_value", "combined"]
SourceType = Literal["csv", "postgres", "json"]
ScanType = Literal["csv", "postgres", "json"]


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_id: str
    source_type: SourceType
    source_name: str
    table_or_file: str
    field_name: str
    pii_type: PIIType
    confidence_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    detection_method: DetectionMethod
    masked_examples: list[str] = Field(default_factory=list, max_length=3)
    sample_count: int = Field(ge=0)
    match_count: int = Field(ge=0)
    suggested_action: str


class ScanResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scan_id: str
    scanner_version: str
    scan_type: ScanType
    source: str
    generated_at: datetime
    raw_pii_uploaded: Literal[False] = False
    findings: list[Finding]

    @field_validator("scan_id")
    @classmethod
    def validate_scan_id(cls, value: str) -> str:
        return str(UUID(value))

    @field_validator("generated_at")
    @classmethod
    def validate_timezone_aware_generated_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("generated_at must be timezone-aware")
        return value


def make_finding_id(
    source_type: str,
    source_name: str,
    table_or_file: str,
    field_name: str,
    pii_type: str,
) -> str:
    stable_key = "\x1f".join([source_type, source_name, table_or_file, field_name, pii_type])
    digest = hashlib.sha256(stable_key.encode("utf-8")).hexdigest()
    return f"fnd_{digest[:24]}"
