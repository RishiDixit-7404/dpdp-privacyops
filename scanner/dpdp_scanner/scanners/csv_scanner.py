from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from dpdp_scanner import __version__
from dpdp_scanner.detectors.base import ColumnNameDetection, ScannerError
from dpdp_scanner.detectors.column_name_detector import ColumnNameDetector
from dpdp_scanner.detectors.regex_detectors import RegexValueDetector
from dpdp_scanner.masking import mask_value
from dpdp_scanner.models import Finding, ScanResult, make_finding_id
from dpdp_scanner.risk import risk_level_for, suggested_action_for


REGEX_CONFIDENCE = 0.85
COMBINED_CONFIDENCE = 0.95
MAX_MASKED_EXAMPLES = 3


def scan_csv(path: Path, sample_size: int = 100) -> ScanResult:
    csv_path = Path(path)
    if not csv_path.is_file():
        raise ScannerError("CSV path does not exist or is not a file.")

    try:
        frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False, nrows=sample_size)
    except Exception as exc:  # pragma: no cover - pandas errors vary by parser version
        raise ScannerError("Unable to read CSV file.") from exc

    column_detector = ColumnNameDetector()
    regex_detector = RegexValueDetector()
    findings: list[Finding] = []
    source_name = csv_path.name

    for column_name in frame.columns:
        values = [str(value) for value in frame[column_name].tolist() if str(value).strip()]
        sample_count = len(values)
        column_detections = _column_detections_by_type(column_detector.detect(str(column_name)))
        regex_matches, regex_row_counts = _regex_matches_by_type(regex_detector, values, str(column_name))

        pii_types = list(column_detections.keys())
        for pii_type in regex_matches:
            if pii_type not in column_detections:
                pii_types.append(pii_type)

        for pii_type in pii_types:
            has_column_match = pii_type in column_detections
            has_regex_match = pii_type in regex_matches
            detection_method = _detection_method(has_column_match, has_regex_match)
            confidence_score = _confidence_score(column_detections.get(pii_type), has_regex_match)
            risk_level = risk_level_for(pii_type, str(column_name), detection_method, confidence_score)
            masked_examples = _masked_examples(pii_type, values, regex_matches.get(pii_type, []))
            match_count = regex_row_counts.get(pii_type, sample_count if has_column_match else 0)

            findings.append(
                Finding(
                    finding_id=make_finding_id("csv", source_name, source_name, str(column_name), pii_type),
                    source_type="csv",
                    source_name=source_name,
                    table_or_file=source_name,
                    field_name=str(column_name),
                    pii_type=pii_type,  # type: ignore
                    confidence_score=confidence_score,
                    risk_level=risk_level,  # type: ignore
                    detection_method=detection_method,  # type: ignore
                    masked_examples=masked_examples,
                    sample_count=sample_count,
                    match_count=match_count,
                    suggested_action=suggested_action_for(pii_type, risk_level, str(column_name)),
                )
            )

    return ScanResult(
        scan_id=str(uuid4()),
        scanner_version=__version__,
        scan_type="csv",
        source=source_name,
        generated_at=datetime.now(timezone.utc),
        raw_pii_uploaded=False,
        findings=findings,
    )


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
    column_name: str,
) -> tuple[dict[str, list[str]], dict[str, int]]:
    matches_by_type: dict[str, list[str]] = defaultdict(list)
    row_counts: dict[str, int] = defaultdict(int)

    for value in values:
        seen_in_row: set[str] = set()
        for detection in detector.detect(value, column_name=column_name):
            matches_by_type[detection.pii_type].extend(detection.matches)
            seen_in_row.add(detection.pii_type)
        for pii_type in seen_in_row:
            row_counts[pii_type] += 1

    return dict(matches_by_type), dict(row_counts)


def _detection_method(has_column_match: bool, has_regex_match: bool) -> str:
    if has_column_match and has_regex_match:
        return "combined"
    if has_regex_match:
        return "regex_value"
    return "column_name"


def _confidence_score(column_detection: ColumnNameDetection | None, has_regex_match: bool) -> float:
    if column_detection and has_regex_match:
        return COMBINED_CONFIDENCE
    if has_regex_match:
        return REGEX_CONFIDENCE
    if column_detection:
        return column_detection.confidence_score
    return 0.0


def _masked_examples(pii_type: str, values: list[str], raw_matches: list[str]) -> list[str]:
    examples: list[str] = []

    source_values = raw_matches if raw_matches else values
    for value in source_values:
        masked = mask_value(value, pii_type)
        if masked and masked not in examples:
            examples.append(masked)
        if len(examples) >= MAX_MASKED_EXAMPLES:
            break

    return examples
