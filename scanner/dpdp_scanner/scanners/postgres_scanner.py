from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse
from uuid import uuid4

import psycopg

from dpdp_scanner import __version__
from dpdp_scanner.detectors.base import ScannerError
from dpdp_scanner.detectors.column_name_detector import ColumnNameDetector
from dpdp_scanner.models import Finding, ScanResult, make_finding_id
from dpdp_scanner.risk import risk_level_for, suggested_action_for


METADATA_QUERY = """
select table_schema, table_name, column_name, data_type
from information_schema.columns
where table_schema not in ('pg_catalog', 'information_schema')
order by table_schema, table_name, ordinal_position
"""


def scan_postgres_metadata(database_url: str) -> ScanResult:
    detector = ColumnNameDetector()
    source = _safe_postgres_source(database_url)
    findings: list[Finding] = []

    try:
        with psycopg.connect(database_url, connect_timeout=10) as connection:
            with connection.cursor() as cursor:
                cursor.execute(METADATA_QUERY)
                rows = cursor.fetchall()
    except Exception as exc:
        raise ScannerError("Unable to connect to Postgres or read metadata.") from exc

    for schema_name, table_name, column_name, data_type in rows:
        table_ref = f"{schema_name}.{table_name}"
        detections = detector.detect(
            str(column_name),
            context_names=[str(schema_name), str(table_name), str(data_type)],
        )
        for detection in detections:
            risk_level = risk_level_for(
                detection.pii_type,
                str(column_name),
                "column_name",
                detection.confidence_score,
            )
            findings.append(
                Finding(
                    finding_id=make_finding_id("postgres", source, table_ref, str(column_name), detection.pii_type),
                    source_type="postgres",
                    source_name=source,
                    table_or_file=table_ref,
                    field_name=str(column_name),
                    pii_type=detection.pii_type,
                    confidence_score=detection.confidence_score,
                    risk_level=risk_level,
                    detection_method="column_name",
                    masked_examples=[],
                    sample_count=0,
                    match_count=0,
                    suggested_action=suggested_action_for(detection.pii_type, risk_level, str(column_name)),
                )
            )

    return ScanResult(
        scan_id=str(uuid4()),
        scanner_version=__version__,
        scan_type="postgres",
        source=source,
        generated_at=datetime.now(timezone.utc),
        raw_pii_uploaded=False,
        findings=findings,
    )


def _safe_postgres_source(database_url: str) -> str:
    parsed = urlparse(database_url)
    host = parsed.hostname or "postgres"
    database = parsed.path.lstrip("/") or "database"
    return f"{host}/{database}"
