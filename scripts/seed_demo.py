from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sys
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'dpdp_privacyops_dev.db'}")
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import models  # noqa: E402
from app.database import SessionLocal  # noqa: E402


ORG_ID = UUID("11111111-1111-4111-8111-111111111111")
PROJECT_ID = UUID("22222222-2222-4222-8222-222222222222")
SCAN_ID = UUID("33333333-3333-4333-8333-333333333333")
ACCESS_REQUEST_ID = UUID("44444444-4444-4444-8444-444444444444")
DELETION_REQUEST_ID = UUID("55555555-5555-4555-8555-555555555555")
GRIEVANCE_REQUEST_ID = UUID("66666666-6666-4666-8666-666666666666")
CONSENT_EVENT_IDS = [
    UUID("77777777-7777-4777-8777-777777777771"),
    UUID("77777777-7777-4777-8777-777777777772"),
    UUID("77777777-7777-4777-8777-777777777773"),
    UUID("77777777-7777-4777-8777-777777777774"),
]
GENERATED_AT = datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc)


def main() -> None:
    db = SessionLocal()
    try:
        organization = db.get(models.Organization, ORG_ID)
        if organization is None:
            organization = models.Organization(id=ORG_ID, name="Acme EdTech", created_at=GENERATED_AT)
            db.add(organization)
        else:
            organization.name = "Acme EdTech"

        project = db.get(models.Project, PROJECT_ID)
        if project is None:
            project = models.Project(
                id=PROJECT_ID,
                organization_id=ORG_ID,
                name="Learno AI Tutor",
                description="Local MVP demo project for India-first DPDP technical readiness evidence.",
                created_at=GENERATED_AT,
            )
            db.add(project)
        else:
            project.organization_id = ORG_ID
            project.name = "Learno AI Tutor"
            project.description = "Local MVP demo project for India-first DPDP technical readiness evidence."

        _reset_demo_rows(db)
        _seed_scan(db)
        _seed_data_requests(db)
        _seed_consent_events(db)
        db.commit()
    finally:
        db.close()

    print("PASS seeded Acme EdTech / Learno AI Tutor demo metadata")
    print(f"PASS demo project id: {PROJECT_ID}")


def _reset_demo_rows(db) -> None:
    for event_id in CONSENT_EVENT_IDS:
        event = db.get(models.ConsentEvent, event_id)
        if event is not None:
            db.delete(event)

    for request_id in [ACCESS_REQUEST_ID, DELETION_REQUEST_ID, GRIEVANCE_REQUEST_ID]:
        data_request = db.get(models.DataRequest, request_id)
        if data_request is not None:
            db.delete(data_request)

    scan = db.get(models.Scan, SCAN_ID)
    if scan is not None:
        db.delete(scan)
    db.flush()


def _seed_scan(db) -> None:
    scan = models.Scan(
        id=SCAN_ID,
        project_id=PROJECT_ID,
        scanner_scan_id="demo-learno-ai-tutor-2026-04-30",
        scanner_version="0.1.0",
        scan_type="json",
        source="learno-demo-safe-metadata.json",
        generated_at=GENERATED_AT,
        raw_pii_uploaded=False,
        created_at=GENERATED_AT,
    )
    db.add(scan)
    db.flush()

    findings = [
        {
            "scanner_finding_id": "demo_users_email",
            "source_type": "postgres",
            "source_name": "learno-postgres",
            "table_or_file": "users",
            "field_name": "email",
            "pii_type": "contact_data",
            "confidence_score": 0.98,
            "risk_level": "high",
            "detection_method": "combined",
            "masked_examples": ["r***@example.com"],
            "sample_count": 100,
            "match_count": 96,
            "suggested_action": "Classify as contact data and confirm purpose, retention, and access controls.",
        },
        {
            "scanner_finding_id": "demo_users_phone",
            "source_type": "postgres",
            "source_name": "learno-postgres",
            "table_or_file": "users",
            "field_name": "phone",
            "pii_type": "contact_data",
            "confidence_score": 0.97,
            "risk_level": "high",
            "detection_method": "combined",
            "masked_examples": ["98******10"],
            "sample_count": 100,
            "match_count": 91,
            "suggested_action": "Classify as contact data and verify minimization for messaging workflows.",
        },
        {
            "scanner_finding_id": "demo_students_date_of_birth",
            "source_type": "postgres",
            "source_name": "learno-postgres",
            "table_or_file": "students",
            "field_name": "date_of_birth",
            "pii_type": "student_or_child_data",
            "confidence_score": 0.96,
            "risk_level": "high",
            "detection_method": "column_name",
            "masked_examples": ["student_****"],
            "sample_count": 80,
            "match_count": 80,
            "suggested_action": "Treat as student or child data and document access restrictions and retention.",
        },
        {
            "scanner_finding_id": "demo_support_ticket_body",
            "source_type": "postgres",
            "source_name": "supportdesk-export",
            "table_or_file": "support_tickets",
            "field_name": "ticket_body",
            "pii_type": "free_text_possible_pii",
            "confidence_score": 0.84,
            "risk_level": "high",
            "detection_method": "combined",
            "masked_examples": ["ABC*****F", "parent_****"],
            "sample_count": 50,
            "match_count": 13,
            "suggested_action": "Add support-ticket redaction and staff handling guidance before storage.",
        },
        {
            "scanner_finding_id": "demo_activity_logs_payload",
            "source_type": "json",
            "source_name": "activity-logs-jsonl",
            "table_or_file": "activity_logs",
            "field_name": "payload",
            "pii_type": "free_text_possible_pii",
            "confidence_score": 0.93,
            "risk_level": "critical",
            "detection_method": "combined",
            "masked_examples": ["r***@example.com", "98******10"],
            "sample_count": 200,
            "match_count": 31,
            "suggested_action": "Add redaction before log ingestion and restrict log search access.",
        },
        {
            "scanner_finding_id": "demo_ai_tutor_prompts_input_text",
            "source_type": "json",
            "source_name": "ai-tutor-prompts-json",
            "table_or_file": "ai_tutor_prompts",
            "field_name": "input_text",
            "pii_type": "student_or_child_data",
            "confidence_score": 0.94,
            "risk_level": "critical",
            "detection_method": "combined",
            "masked_examples": ["student_****", "parent_****"],
            "sample_count": 120,
            "match_count": 24,
            "suggested_action": "Add prompt redaction and policy checks before AI tutor processing.",
        },
    ]
    for item in findings:
        db.add(models.Finding(scan_id=SCAN_ID, created_at=GENERATED_AT, **item))


def _seed_data_requests(db) -> None:
    requests = [
        (
            ACCESS_REQUEST_ID,
            "access",
            "student_****",
            "Demo seed: Access request for learner profile export evidence.",
            GENERATED_AT + timedelta(minutes=20),
        ),
        (
            DELETION_REQUEST_ID,
            "deletion",
            "parent_****",
            "Demo seed: Deletion request for account closure workflow evidence.",
            GENERATED_AT + timedelta(minutes=30),
        ),
        (
            GRIEVANCE_REQUEST_ID,
            "grievance",
            "student_****",
            "Demo seed: Grievance request for privacy operations workflow evidence.",
            GENERATED_AT + timedelta(minutes=40),
        ),
    ]
    for request_id, request_type, identifier, details, created_at in requests:
        data_request = models.DataRequest(
            id=request_id,
            project_id=PROJECT_ID,
            request_type=request_type,
            status="new",
            requester_name=None,
            requester_email="r***@example.com",
            requester_identifier=identifier,
            request_details=details,
            due_date=created_at + timedelta(days=14),
            assigned_to="privacy-ops",
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(data_request)
        db.flush()
        db.add(
            models.DataRequestAuditEvent(
                data_request_id=request_id,
                event_type="created",
                message="Demo User Data Request created.",
                event_metadata={"seed": "local_mvp_demo", "request_type": request_type},
                created_at=created_at,
            )
        )


def _seed_consent_events(db) -> None:
    events = [
        ("student_****", "marketing_whatsapp", "granted", GENERATED_AT + timedelta(minutes=50)),
        ("student_****", "marketing_whatsapp", "withdrawn", GENERATED_AT + timedelta(minutes=60)),
        ("student_****", "ai_tutor_personalisation", "granted", GENERATED_AT + timedelta(minutes=70)),
        ("parent_****", "product_analytics", "granted", GENERATED_AT + timedelta(minutes=80)),
    ]
    for event_id, (external_user_id, purpose, status, occurred_at) in zip(CONSENT_EVENT_IDS, events, strict=True):
        db.add(
            models.ConsentEvent(
                id=event_id,
                project_id=PROJECT_ID,
                external_user_id=external_user_id,
                purpose=purpose,
                status=status,
                notice_version="demo-v1",
                source="demo_seed",
                occurred_at=occurred_at,
                event_metadata={"seed": "local_mvp_demo"},
                created_at=occurred_at,
            )
        )


if __name__ == "__main__":
    main()
