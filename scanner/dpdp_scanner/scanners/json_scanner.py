from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import json
from json import JSONDecodeError
from pathlib import Path
from uuid import uuid4

from dpdp_scanner import __version__
from dpdp_scanner.detectors.base import ColumnNameDetection, ScannerError
from dpdp_scanner.detectors.column_name_detector import ColumnNameDetector, identifier_tokens, normalize_identifier
from dpdp_scanner.detectors.regex_detectors import RegexValueDetector
from dpdp_scanner.masking import mask_value
from dpdp_scanner.models import Finding, ScanResult, make_finding_id
from dpdp_scanner.risk import FREE_TEXT_CONTAINER_FIELDS, risk_level_for, suggested_action_for


SUPPORTED_JSON_EXTENSIONS = {".json", ".jsonl"}
REGEX_CONFIDENCE = 0.85
COMBINED_CONFIDENCE = 0.95
MAX_MASKED_EXAMPLES = 3


def scan_json(path: Path, sample_size: int = 100) -> ScanResult:
    json_path = Path(path)
    if not json_path.is_file():
        raise ScannerError("JSON path does not exist or is not a file.")
    if json_path.suffix.lower() not in SUPPORTED_JSON_EXTENSIONS:
        raise ScannerError("Unsupported JSON scanner input. Use a .json or .jsonl file.")

    records = _load_records(json_path, sample_size)
    source_name = json_path.name
    values_by_path = _values_by_path(records, sample_size)
    findings = _findings_for_paths(values_by_path, source_name)

    return ScanResult(
        scan_id=str(uuid4()),
        scanner_version=__version__,
        scan_type="json",
        source=source_name,
        generated_at=datetime.now(timezone.utc),
        raw_pii_uploaded=False,
        findings=findings,
    )


def flatten_json(value: object, path: str = "") -> list[tuple[str, str]]:
    if isinstance(value, dict):
        flattened: list[tuple[str, str]] = []
        for key, nested_value in value.items():
            child_path = str(key) if not path else f"{path}.{key}"
            flattened.extend(flatten_json(nested_value, child_path))
        return flattened

    if isinstance(value, list):
        array_path = f"{path}[]" if path else "[]"
        flattened = []
        for item in value:
            flattened.extend(flatten_json(item, array_path))
        return flattened

    if value is None or isinstance(value, bool):
        return []

    scalar_path = path or "value"
    scalar_value = str(value)
    if not scalar_value.strip():
        return []
    return [(scalar_path, scalar_value)]


def _load_records(path: Path, sample_size: int) -> list[object]:
    if path.suffix.lower() == ".jsonl":
        return _load_jsonl_records(path, sample_size)
    return _load_json_records(path, sample_size)


def _load_json_records(path: Path, sample_size: int) -> list[object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except JSONDecodeError as exc:
        raise ScannerError(f"Invalid JSON file at line {exc.lineno}, column {exc.colno}.") from exc
    except UnicodeDecodeError as exc:
        raise ScannerError("Unable to read JSON file as UTF-8.") from exc

    if isinstance(data, list):
        return data[:sample_size]
    return [data]


def _load_jsonl_records(path: Path, sample_size: int) -> list[object]:
    records: list[object] = []
    try:
        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if len(records) >= sample_size:
                    break
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except JSONDecodeError as exc:
                    raise ScannerError(
                        f"Invalid JSONL file at line {line_number}, column {exc.colno}."
                    ) from exc
                if not isinstance(record, dict):
                    raise ScannerError(f"Invalid JSONL record at line {line_number}: expected object.")
                records.append(record)
    except UnicodeDecodeError as exc:
        raise ScannerError("Unable to read JSONL file as UTF-8.") from exc
    return records


def _values_by_path(records: list[object], sample_size: int) -> dict[str, list[str]]:
    values_by_path: dict[str, list[str]] = defaultdict(list)
    for record in records:
        for field_path, value in flatten_json(record):
            if len(values_by_path[field_path]) < sample_size:
                values_by_path[field_path].append(value)
    return dict(values_by_path)


def _findings_for_paths(values_by_path: dict[str, list[str]], source_name: str) -> list[Finding]:
    column_detector = ColumnNameDetector()
    regex_detector = RegexValueDetector()
    findings: list[Finding] = []

    for field_path, values in values_by_path.items():
        sample_count = len(values)
        final_key = _final_path_key(field_path)
        context_names = [field_path, *_path_contexts(field_path)]
        column_detections = _column_detections_by_type(column_detector.detect(final_key, context_names=context_names))
        regex_matches, regex_row_counts = _regex_matches_by_type(regex_detector, values, field_path)
        is_free_text_path = _is_free_text_path(field_path) or "free_text_possible_pii" in column_detections

        pii_types = list(column_detections.keys())
        for pii_type in regex_matches:
            if pii_type not in column_detections:
                pii_types.append(pii_type)

        for pii_type in pii_types:
            has_column_match = pii_type in column_detections
            has_regex_match = pii_type in regex_matches
            combined_via_free_text = has_regex_match and is_free_text_path
            detection_method = _detection_method(has_column_match or combined_via_free_text, has_regex_match)
            confidence_score = _confidence_score(column_detections.get(pii_type), has_regex_match, combined_via_free_text)
            risk_level = risk_level_for(pii_type, field_path, detection_method, confidence_score)
            masked_examples = _masked_examples(
                pii_type=pii_type,
                values=values,
                raw_matches=regex_matches.get(pii_type, []),
                is_free_text_path=is_free_text_path,
            )
            match_count = regex_row_counts.get(pii_type, sample_count if has_column_match else 0)

            findings.append(
                Finding(
                    finding_id=make_finding_id("json", source_name, source_name, field_path, pii_type),
                    source_type="json",
                    source_name=source_name,
                    table_or_file=source_name,
                    field_name=field_path,
                    pii_type=pii_type,
                    confidence_score=confidence_score,
                    risk_level=risk_level,
                    detection_method=detection_method,
                    masked_examples=masked_examples,
                    sample_count=sample_count,
                    match_count=match_count,
                    suggested_action=suggested_action_for(pii_type, risk_level, field_path),
                )
            )

    return findings


def _column_detections_by_type(detections: list[ColumnNameDetection]) -> dict[str, ColumnNameDetection]:
    by_type: dict[str, ColumnNameDetection] = {}
    for detection in detections:
        existing = by_type.get(detection.pii_type)
        if existing is None or detection.confidence_score > existing.confidence_score:
            by_type[detection.pii_type] = detection
    return by_type


def _regex_matches_by_type(
    detector: RegexValueDetector,
    values: list[str],
    field_path: str,
) -> tuple[dict[str, list[str]], dict[str, int]]:
    matches_by_type: dict[str, list[str]] = defaultdict(list)
    row_counts: dict[str, int] = defaultdict(int)

    for value in values:
        seen_in_value: set[str] = set()
        for detection in detector.detect(value, column_name=field_path):
            matches_by_type[detection.pii_type].extend(detection.matches)
            seen_in_value.add(detection.pii_type)
        for pii_type in seen_in_value:
            row_counts[pii_type] += 1

    return dict(matches_by_type), dict(row_counts)


def _detection_method(has_column_match: bool, has_regex_match: bool) -> str:
    if has_column_match and has_regex_match:
        return "combined"
    if has_regex_match:
        return "regex_value"
    return "column_name"


def _confidence_score(
    column_detection: ColumnNameDetection | None,
    has_regex_match: bool,
    combined_via_free_text: bool,
) -> float:
    if (column_detection and has_regex_match) or combined_via_free_text:
        return COMBINED_CONFIDENCE
    if has_regex_match:
        return REGEX_CONFIDENCE
    if column_detection:
        return column_detection.confidence_score
    return 0.0


def _masked_examples(
    pii_type: str,
    values: list[str],
    raw_matches: list[str],
    is_free_text_path: bool,
) -> list[str]:
    examples: list[str] = []

    if raw_matches and is_free_text_path:
        for raw_match in raw_matches:
            masked = mask_value(raw_match, pii_type)
            example = f"[masked free text with {pii_type}: {masked}]"
            if example not in examples:
                examples.append(example)
            if len(examples) >= MAX_MASKED_EXAMPLES:
                return examples

    source_values = raw_matches if raw_matches else values
    for value in source_values:
        masked = mask_value(value, pii_type)
        if masked and masked not in examples:
            examples.append(masked)
        if len(examples) >= MAX_MASKED_EXAMPLES:
            break

    return examples


def _final_path_key(field_path: str) -> str:
    final_part = field_path.split(".")[-1]
    return final_part.removesuffix("[]")


def _path_contexts(field_path: str) -> list[str]:
    clean_parts = [part.removesuffix("[]") for part in field_path.split(".") if part]
    return clean_parts[:-1]


def _is_free_text_path(field_path: str) -> bool:
    normalized_field = normalize_identifier(field_path)
    tokens = identifier_tokens(field_path)
    normalized_with_boundaries = f"_{normalized_field}_"
    return any(
        name in tokens
        or normalized_field == name
        or f"_{name}_" in normalized_with_boundaries
        for name in FREE_TEXT_CONTAINER_FIELDS
    )
