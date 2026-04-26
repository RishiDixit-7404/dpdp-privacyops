from __future__ import annotations

from collections.abc import Generator
import os
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


REPO_ROOT = Path(__file__).resolve().parents[3]
SCANNER_PACKAGE_PATH = REPO_ROOT / "scanner"
if str(SCANNER_PACKAGE_PATH) not in sys.path:
    sys.path.insert(0, str(SCANNER_PACKAGE_PATH))


def _test_database_url() -> str:
    return os.getenv("BACKEND_TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")


def _engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    return {}


database_url = _test_database_url()
engine = create_engine(database_url, future=True, **_engine_kwargs(database_url))
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def project_id(client: TestClient) -> str:
    response = client.post(
        "/projects",
        json={
            "organization_name": "Acme",
            "project_name": "Main App",
            "description": "Primary product",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def scanner_payload(scan_id: str = "scanner-scan-001") -> dict[str, object]:
    return {
        "scan_id": scan_id,
        "scanner_version": "0.1.0",
        "scan_type": "json",
        "source": "sample_logs.jsonl",
        "generated_at": "2026-04-26T10:00:00Z",
        "raw_pii_uploaded": False,
        "findings": [
            {
                "finding_id": "fnd_email",
                "source_type": "json",
                "source_name": "sample_logs.jsonl",
                "table_or_file": "sample_logs.jsonl",
                "field_name": "user.email",
                "pii_type": "email",
                "confidence_score": 0.95,
                "risk_level": "high",
                "detection_method": "combined",
                "masked_examples": ["r*********@example.com"],
                "sample_count": 10,
                "match_count": 9,
                "suggested_action": "Classify this field as contact data.",
            },
            {
                "finding_id": "fnd_aadhaar",
                "source_type": "json",
                "source_name": "sample_logs.jsonl",
                "table_or_file": "sample_logs.jsonl",
                "field_name": "logs.metadata.aadhaar",
                "pii_type": "aadhaar",
                "confidence_score": 0.98,
                "risk_level": "critical",
                "detection_method": "combined",
                "masked_examples": ["**** **** 9012"],
                "sample_count": 10,
                "match_count": 2,
                "suggested_action": "Avoid storing this identifier unless strictly required.",
            },
            {
                "finding_id": "fnd_pan",
                "source_type": "json",
                "source_name": "sample_logs.jsonl",
                "table_or_file": "sample_logs.jsonl",
                "field_name": "ticket.ticket_body",
                "pii_type": "pan",
                "confidence_score": 0.88,
                "risk_level": "critical",
                "detection_method": "combined",
                "masked_examples": ["ABC********"],
                "sample_count": 10,
                "match_count": 1,
                "suggested_action": "Add redaction before log, support-ticket, or prompt ingestion.",
            },
            {
                "finding_id": "fnd_name",
                "source_type": "json",
                "source_name": "sample_logs.jsonl",
                "table_or_file": "sample_logs.jsonl",
                "field_name": "user.name",
                "pii_type": "person_name",
                "confidence_score": 0.75,
                "risk_level": "medium",
                "detection_method": "column_name",
                "masked_examples": ["Ra********ma"],
                "sample_count": 10,
                "match_count": 10,
                "suggested_action": "Classify this field as personal data.",
            },
        ],
    }
