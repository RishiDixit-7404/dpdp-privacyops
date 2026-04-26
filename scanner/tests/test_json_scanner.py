import json
from pathlib import Path
from uuid import UUID

import pytest

from dpdp_scanner.detectors.base import ScannerError
from dpdp_scanner.scanners.json_scanner import flatten_json, scan_json


FIXTURE_DIR = Path(__file__).parent / "fixtures"
LOGS_FIXTURE = FIXTURE_DIR / "sample_logs.jsonl"
PROMPTS_FIXTURE = FIXTURE_DIR / "sample_prompts.json"


def finding_map(result) -> dict[tuple[str, str], object]:
    return {(finding.field_name, finding.pii_type): finding for finding in result.findings}


def test_jsonl_scanner_output_shape() -> None:
    result = scan_json(LOGS_FIXTURE)
    payload = result.model_dump(mode="json")

    assert UUID(payload["scan_id"])
    assert payload["scanner_version"] == "0.1.0"
    assert payload["scan_type"] == "json"
    assert payload["source"] == "sample_logs.jsonl"
    assert payload["raw_pii_uploaded"] is False
    assert payload["findings"]
    assert payload["findings"][0]["source_type"] == "json"
    assert "finding_id" in payload["findings"][0]


def test_json_scanner_output_shape() -> None:
    result = scan_json(PROMPTS_FIXTURE)
    payload = result.model_dump(mode="json")

    assert payload["scan_type"] == "json"
    assert payload["source"] == "sample_prompts.json"
    assert payload["raw_pii_uploaded"] is False
    assert payload["findings"]


def test_flatten_json_nested_paths_and_array_normalization() -> None:
    flattened = dict(
        flatten_json(
            {
                "event": "chat_prompt",
                "user": {"email": "rahul@example.com"},
                "messages": [{"text": "hello"}, {"text": "world"}],
                "events": [{"payload": {"input_text": "phone 9876543210"}}],
            }
        )
    )

    assert flattened["event"] == "chat_prompt"
    assert flattened["user.email"] == "rahul@example.com"
    assert flattened["messages[].text"] == "world"
    assert flattened["events[].payload.input_text"] == "phone 9876543210"
    assert "messages[0].text" not in flattened


def test_jsonl_detects_pii_in_nested_fields() -> None:
    result = scan_json(LOGS_FIXTURE)
    findings = finding_map(result)

    assert ("user.email", "email") in findings
    assert ("payload.input_text", "indian_phone") in findings
    assert ("ticket.ticket_body", "pan") in findings
    assert ("logs.metadata.aadhaar", "aadhaar") in findings
    assert ("payment.payload.upi", "upi_id") in findings
    assert ("request.headers.authorization", "authentication_secret") in findings
    assert ("request.headers.x_api_key", "authentication_secret") in findings
    assert ("prompt", "free_text_possible_pii") in findings
    assert ("response", "free_text_possible_pii") in findings


def test_json_detects_array_paths_and_nested_prompt_pii() -> None:
    result = scan_json(PROMPTS_FIXTURE)
    findings = finding_map(result)

    assert ("users[].profile.email", "email") in findings
    assert ("users[].profile.phone", "indian_phone") in findings
    assert ("support.comments[].message", "authentication_secret") in findings
    assert ("events[].payload.request_body", "pan") in findings
    assert ("prompt.input_text", "aadhaar") in findings
    assert ("response.output_text", "upi_id") in findings


def test_free_text_regex_findings_escalate_and_use_redaction_action() -> None:
    result = scan_json(LOGS_FIXTURE)
    findings = finding_map(result)
    phone_finding = findings[("payload.input_text", "indian_phone")]
    aadhaar_finding = findings[("logs.metadata.aadhaar", "aadhaar")]

    assert phone_finding.detection_method == "combined"
    assert phone_finding.confidence_score == 0.95
    assert phone_finding.risk_level == "critical"
    assert "redaction before log, support-ticket, or prompt ingestion" in phone_finding.suggested_action
    assert aadhaar_finding.risk_level == "critical"


def test_json_finding_id_is_stable_across_repeated_scans() -> None:
    first = scan_json(LOGS_FIXTURE)
    second = scan_json(LOGS_FIXTURE)

    first_ids = {
        (finding.source_type, finding.source_name, finding.table_or_file, finding.field_name, finding.pii_type): finding.finding_id
        for finding in first.findings
    }
    second_ids = {
        (finding.source_type, finding.source_name, finding.table_or_file, finding.field_name, finding.pii_type): finding.finding_id
        for finding in second.findings
    }

    assert first_ids == second_ids


@pytest.mark.parametrize(
    ("fixture", "raw_values"),
    [
        (
            LOGS_FIXTURE,
            [
                "rahul.logs@example.com",
                "ananya.logs@example.org",
                "9876543210",
                "ABCDE1234F",
                "1234 5678 9012",
                "rahul@upi",
                "Bearer abcdefghijk123",
                "sk_test_LOGSKEY123456",
                "919876543211",
                "priya.response@example.net",
            ],
        ),
        (
            PROMPTS_FIXTURE,
            [
                "2345 6789 0123",
                "+91 9876543212",
                "ananya@okicici",
                "api_key=promptSecret12345",
                "Kavya Menon",
                "json.user@example.com",
                "919876543212",
                "FGHIJ5678K",
            ],
        ),
    ],
)
def test_no_raw_json_fixture_pii_appears_anywhere_in_serialized_output(
    fixture: Path,
    raw_values: list[str],
) -> None:
    result = scan_json(fixture)
    serialized = json.dumps(result.model_dump(mode="json"))

    for raw_value in raw_values:
        assert raw_value not in serialized


def test_invalid_jsonl_error_does_not_include_raw_line(tmp_path: Path) -> None:
    bad_path = tmp_path / "bad.jsonl"
    bad_path.write_text('{"message": "rahul.logs@example.com"\n', encoding="utf-8")

    with pytest.raises(ScannerError) as error:
        scan_json(bad_path)

    error_text = str(error.value)
    assert "Invalid JSONL file at line 1" in error_text
    assert "rahul.logs@example.com" not in error_text
