from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from dpdp_scanner.models import Finding, ScanResult


def valid_finding(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "finding_id": "fnd_test123",
        "source_type": "csv",
        "source_name": "sample_customers.csv",
        "table_or_file": "sample_customers.csv",
        "field_name": "email",
        "pii_type": "email",
        "confidence_score": 0.95,
        "risk_level": "high",
        "detection_method": "combined",
        "masked_examples": ["r*****@example.com"],
        "sample_count": 2,
        "match_count": 2,
        "suggested_action": "Classify this field as contact data.",
    }
    payload.update(overrides)
    return payload


def valid_scan_result(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "scan_id": str(uuid4()),
        "scanner_version": "0.1.0",
        "scan_type": "csv",
        "source": "sample_customers.csv",
        "generated_at": datetime.now(timezone.utc),
        "raw_pii_uploaded": False,
        "findings": [valid_finding()],
    }
    payload.update(overrides)
    return payload


def test_models_validate_contract_fields() -> None:
    Finding(**valid_finding())
    ScanResult(**valid_scan_result())


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("confidence_score", 1.2),
        ("risk_level", "severe"),
        ("detection_method", "regex"),
        ("source_type", "mysql"),
        ("masked_examples", ["one", "two", "three", "four"]),
    ],
)
def test_finding_rejects_invalid_contract_values(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        Finding(**valid_finding(**{field: value}))


def test_scan_result_requires_raw_pii_uploaded_false() -> None:
    with pytest.raises(ValidationError):
        ScanResult(**valid_scan_result(raw_pii_uploaded=True))


def test_scan_result_requires_timezone_aware_generated_at() -> None:
    with pytest.raises(ValidationError):
        ScanResult(**valid_scan_result(generated_at=datetime(2026, 1, 1, 0, 0, 0)))
