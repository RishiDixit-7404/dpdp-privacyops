import json
from pathlib import Path
from uuid import UUID

from dpdp_scanner.scanners.csv_scanner import scan_csv


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_customers.csv"


def test_csv_scanner_json_output_shape() -> None:
    result = scan_csv(FIXTURE_PATH)
    payload = result.model_dump(mode="json")

    assert UUID(payload["scan_id"])
    assert payload["scanner_version"] == "0.1.0"
    assert payload["scan_type"] == "csv"
    assert payload["source"] == "sample_customers.csv"
    assert payload["raw_pii_uploaded"] is False
    assert payload["findings"]

    required_keys = {
        "finding_id",
        "source_type",
        "source_name",
        "table_or_file",
        "field_name",
        "pii_type",
        "confidence_score",
        "risk_level",
        "detection_method",
        "masked_examples",
        "sample_count",
        "match_count",
        "suggested_action",
    }
    assert required_keys <= set(payload["findings"][0])


def test_csv_scanner_detects_required_pii_types() -> None:
    result = scan_csv(FIXTURE_PATH)
    pii_types = {finding.pii_type for finding in result.findings}

    assert {
        "email",
        "indian_phone",
        "pan",
        "aadhaar",
        "upi_id",
        "date_of_birth",
        "free_text_possible_pii",
        "authentication_secret",
    } <= pii_types


def test_no_raw_pii_appears_anywhere_in_serialized_json_output() -> None:
    result = scan_csv(FIXTURE_PATH)
    payload = result.model_dump(mode="json")
    serialized = json.dumps(payload)

    raw_values = [
        "Rahul Sharma",
        "Ananya Rao",
        "rahul.sharma@example.com",
        "ananya.rao@example.org",
        "+91 9876543210",
        "9876543210",
        "919876543211",
        "ABCDE1234F",
        "FGHIJ5678K",
        "1234 5678 9012",
        "2345 6789 0123",
        "rahul@upi",
        "ananya@okicici",
        "1998-04-15",
        "12/08/2001",
        "Customer asked to update phone 9876543210",
        "Support note with PAN LMNOP1234Q",
        "LMNOP1234Q",
        "Bearer abcdefghijk123",
        "sk_test_FAKEKEY1234567890",
    ]

    for raw_value in raw_values:
        assert raw_value not in serialized


def test_schema_stability_and_privacy_contract() -> None:
    first_result = scan_csv(FIXTURE_PATH)
    second_result = scan_csv(FIXTURE_PATH)

    assert first_result.scan_id
    assert UUID(first_result.scan_id)
    assert first_result.raw_pii_uploaded is False
    assert first_result.generated_at.tzinfo is not None
    assert first_result.generated_at.utcoffset() is not None

    first_finding_ids = {
        (
            finding.source_type,
            finding.source_name,
            finding.table_or_file,
            finding.field_name,
            finding.pii_type,
        ): finding.finding_id
        for finding in first_result.findings
    }
    second_finding_ids = {
        (
            finding.source_type,
            finding.source_name,
            finding.table_or_file,
            finding.field_name,
            finding.pii_type,
        ): finding.finding_id
        for finding in second_result.findings
    }

    assert first_finding_ids == second_finding_ids

    for finding in first_result.findings:
        assert finding.finding_id
        assert len(finding.masked_examples) <= 3
