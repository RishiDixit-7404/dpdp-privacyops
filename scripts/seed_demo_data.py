#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = REPO_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app import models  # noqa: E402
from app.database import SessionLocal, settings  # noqa: E402


DEMO_ORGANIZATION_NAME = "Acme EdTech Demo"
DEMO_PROJECT_NAME = "Student Learning Platform"
DEMO_SCANNER_SCAN_ID = "demo-student-learning-platform-v1"
DEMO_SOURCE = "demo_student_platform_logs.jsonl"
DEMO_USER_IDS = ("usr_demo_001", "usr_demo_002", "usr_demo_003", "usr_demo_004")
DEMO_GENERATED_AT = datetime(2026, 4, 26, 9, 30, tzinfo=timezone.utc)


DEMO_FINDINGS: list[dict[str, Any]] = [
    {
        "scanner_finding_id": "demo_fnd_support_aadhaar",
        "source_type": "json",
        "source_name": DEMO_SOURCE,
        "table_or_file": DEMO_SOURCE,
        "field_name": "support_tickets.ticket_body",
        "pii_type": "aadhaar",
        "confidence_score": 0.95,
        "risk_level": "critical",
        "detection_method": "combined",
        "masked_examples": ["Support note includes **** **** 4321"],
        "sample_count": 25,
        "match_count": 3,
        "suggested_action": "Redact Aadhaar-like identifiers before support-ticket ingestion and restrict access to retained records.",
    },
    {
        "scanner_finding_id": "demo_fnd_activity_secret",
        "source_type": "json",
        "source_name": DEMO_SOURCE,
        "table_or_file": DEMO_SOURCE,
        "field_name": "activity_logs.request_body",
        "pii_type": "authentication_secret",
        "confidence_score": 0.97,
        "risk_level": "critical",
        "detection_method": "combined",
        "masked_examples": ["Bearer sk************"],
        "sample_count": 25,
        "match_count": 2,
        "suggested_action": "Remove secrets from logs immediately, rotate exposed credentials, and add request-body redaction.",
    },
    {
        "scanner_finding_id": "demo_fnd_finance_pan_payload",
        "source_type": "json",
        "source_name": DEMO_SOURCE,
        "table_or_file": DEMO_SOURCE,
        "field_name": "finance_exports.audit_payload",
        "pii_type": "pan",
        "confidence_score": 0.92,
        "risk_level": "critical",
        "detection_method": "combined",
        "masked_examples": ["PAN ABC********"],
        "sample_count": 25,
        "match_count": 2,
        "suggested_action": "Review PAN storage and retention, tokenize where possible, and redact finance payload logs.",
    },
    {
        "scanner_finding_id": "demo_fnd_ai_prompt_phone",
        "source_type": "json",
        "source_name": DEMO_SOURCE,
        "table_or_file": DEMO_SOURCE,
        "field_name": "ai_tutor_prompts.input_text",
        "pii_type": "indian_phone",
        "confidence_score": 0.95,
        "risk_level": "critical",
        "detection_method": "combined",
        "masked_examples": ["Parent phone in prompt: 98******21"],
        "sample_count": 25,
        "match_count": 4,
        "suggested_action": "Add redaction before AI prompt ingestion and avoid storing contact data in prompt logs.",
    },
    {
        "scanner_finding_id": "demo_fnd_users_email",
        "source_type": "json",
        "source_name": DEMO_SOURCE,
        "table_or_file": DEMO_SOURCE,
        "field_name": "users.email",
        "pii_type": "email",
        "confidence_score": 0.95,
        "risk_level": "high",
        "detection_method": "combined",
        "masked_examples": ["l***********@example.test", "p*********@example.test"],
        "sample_count": 25,
        "match_count": 24,
        "suggested_action": "Classify as contact data and ensure access controls, retention rules, and deletion workflow coverage.",
    },
    {
        "scanner_finding_id": "demo_fnd_parent_phone",
        "source_type": "json",
        "source_name": DEMO_SOURCE,
        "table_or_file": DEMO_SOURCE,
        "field_name": "students.parent_phone",
        "pii_type": "indian_phone",
        "confidence_score": 0.95,
        "risk_level": "high",
        "detection_method": "combined",
        "masked_examples": ["98******21", "+91 99******30"],
        "sample_count": 25,
        "match_count": 22,
        "suggested_action": "Classify as contact data and restrict staff access to parent contact fields.",
    },
    {
        "scanner_finding_id": "demo_fnd_student_dob",
        "source_type": "json",
        "source_name": DEMO_SOURCE,
        "table_or_file": DEMO_SOURCE,
        "field_name": "students.date_of_birth",
        "pii_type": "student_or_child_data",
        "confidence_score": 0.9,
        "risk_level": "high",
        "detection_method": "combined",
        "masked_examples": ["20**-**-14", "20**-**-02"],
        "sample_count": 25,
        "match_count": 25,
        "suggested_action": "Mark as a high-risk student data flow and review retention and role-based access.",
    },
    {
        "scanner_finding_id": "demo_fnd_payments_upi",
        "source_type": "json",
        "source_name": DEMO_SOURCE,
        "table_or_file": DEMO_SOURCE,
        "field_name": "payments.vpa",
        "pii_type": "upi_id",
        "confidence_score": 0.88,
        "risk_level": "high",
        "detection_method": "combined",
        "masked_examples": ["p********@upi"],
        "sample_count": 25,
        "match_count": 7,
        "suggested_action": "Classify payment identifiers as financial data and restrict operational access.",
    },
    {
        "scanner_finding_id": "demo_fnd_student_name",
        "source_type": "json",
        "source_name": DEMO_SOURCE,
        "table_or_file": DEMO_SOURCE,
        "field_name": "students.student_name",
        "pii_type": "person_name",
        "confidence_score": 0.75,
        "risk_level": "medium",
        "detection_method": "column_name",
        "masked_examples": ["Ar******ao", "Mi******ah"],
        "sample_count": 25,
        "match_count": 25,
        "suggested_action": "Classify as personal data and include this field in access and deletion workflows.",
    },
    {
        "scanner_finding_id": "demo_fnd_student_address",
        "source_type": "json",
        "source_name": DEMO_SOURCE,
        "table_or_file": DEMO_SOURCE,
        "field_name": "students.home_address",
        "pii_type": "address",
        "confidence_score": 0.75,
        "risk_level": "medium",
        "detection_method": "column_name",
        "masked_examples": ["Bl**********al", "Pu**********ne"],
        "sample_count": 25,
        "match_count": 18,
        "suggested_action": "Classify as address data and apply retention and access controls.",
    },
]


def main() -> None:
    print(f"Using database: {settings.database_url}")
    with SessionLocal() as db:
        organization, project, created_project = _get_or_create_demo_project(db)
        scan_created = _ensure_demo_scan(db, project)
        _replace_demo_data_requests(db, project)
        _replace_demo_consent_events(db, project)
        db.commit()

        print("")
        print("Demo seed complete.")
        print(f"Organization: {organization.name}")
        print(f"Project: {project.name} ({project.id})")
        print(f"Project created: {'yes' if created_project else 'no, reused existing project'}")
        print(f"Scanner scan created: {'yes' if scan_created else 'no, reused existing demo scan'}")
        print("")
        print("Demo URLs:")
        print("  Projects:              http://localhost:3000/projects")
        print(f"  Project detail:         http://localhost:3000/projects/{project.id}")
        print(f"  User Data Requests:    http://localhost:3000/projects/{project.id}/requests")
        print(f"  Consent Events:        http://localhost:3000/projects/{project.id}/consent")
        print(f"  Evidence Report:       http://localhost:3000/projects/{project.id}/evidence-report")
        print(f"  Public Privacy Request: http://localhost:3000/public/projects/{project.id}/privacy-request")


def _get_or_create_demo_project(db: Session) -> tuple[models.Organization, models.Project, bool]:
    organization = db.scalar(select(models.Organization).where(models.Organization.name == DEMO_ORGANIZATION_NAME))
    if organization is None:
        organization = models.Organization(name=DEMO_ORGANIZATION_NAME)
        db.add(organization)
        db.flush()

    project = db.scalar(
        select(models.Project).where(
            models.Project.organization_id == organization.id,
            models.Project.name == DEMO_PROJECT_NAME,
        )
    )
    if project is not None:
        return organization, project, False

    project = models.Project(
        organization_id=organization.id,
        name=DEMO_PROJECT_NAME,
        description="Demo edtech project for local DPDP PrivacyOps walkthroughs.",
    )
    db.add(project)
    db.flush()
    return organization, project, True


def _ensure_demo_scan(db: Session, project: models.Project) -> bool:
    existing_scan = db.scalar(select(models.Scan).where(models.Scan.scanner_scan_id == DEMO_SCANNER_SCAN_ID))
    if existing_scan is not None:
        return False

    scan = models.Scan(
        project_id=project.id,
        scanner_scan_id=DEMO_SCANNER_SCAN_ID,
        scanner_version="0.1.0",
        scan_type="json",
        source=DEMO_SOURCE,
        generated_at=DEMO_GENERATED_AT,
        raw_pii_uploaded=False,
    )
    db.add(scan)
    db.flush()

    for item in DEMO_FINDINGS:
        db.add(models.Finding(scan_id=scan.id, **item))
    return True


def _replace_demo_data_requests(db: Session, project: models.Project) -> None:
    existing = list(
        db.scalars(
            select(models.DataRequest).where(
                models.DataRequest.project_id == project.id,
                models.DataRequest.requester_identifier.in_(DEMO_USER_IDS),
            )
        ).all()
    )
    for data_request in existing:
        db.delete(data_request)
    db.flush()

    requests = [
        {
            "request_type": "access",
            "status": "new",
            "requester_name": "Learner One",
            "requester_email": "learner.one@example.test",
            "requester_identifier": "usr_demo_001",
            "request_details": "Please send a copy of my learning profile and support history.",
            "due_date": datetime(2026, 4, 20, 10, 0, tzinfo=timezone.utc),
            "assigned_to": "privacy-ops",
        },
        {
            "request_type": "deletion",
            "status": "in_progress",
            "requester_name": "Parent Two",
            "requester_email": "parent.two@example.test",
            "requester_identifier": "usr_demo_002",
            "request_details": "Please delete the inactive student account after verification.",
            "due_date": datetime(2026, 5, 5, 10, 0, tzinfo=timezone.utc),
            "assigned_to": "support-lead",
        },
        {
            "request_type": "grievance",
            "status": "verifying",
            "requester_name": "Guardian Three",
            "requester_email": "guardian.three@example.test",
            "requester_identifier": "usr_demo_003",
            "request_details": "I want to understand why tutoring messages were retained.",
            "due_date": datetime(2026, 5, 3, 10, 0, tzinfo=timezone.utc),
            "assigned_to": "privacy-ops",
        },
        {
            "request_type": "correction",
            "status": "completed",
            "requester_name": "Learner Four",
            "requester_email": "learner.four@example.test",
            "requester_identifier": "usr_demo_004",
            "request_details": "Correct the class grade on my student profile.",
            "due_date": datetime(2026, 4, 18, 10, 0, tzinfo=timezone.utc),
            "assigned_to": "student-success",
            "completed_at": datetime(2026, 4, 17, 12, 0, tzinfo=timezone.utc),
        },
    ]

    created_requests: list[models.DataRequest] = []
    for item in requests:
        completed_at = item.pop("completed_at", None)
        data_request = models.DataRequest(project_id=project.id, completed_at=completed_at, **item)
        db.add(data_request)
        db.flush()
        created_requests.append(data_request)
        _add_audit_event(db, data_request.id, "created", "Demo User Data Request created.", {"request_type": data_request.request_type})
        if data_request.status != "new":
            _add_audit_event(
                db,
                data_request.id,
                "status_changed",
                f"Status changed from new to {data_request.status}.",
                {"from": "new", "to": data_request.status},
            )
        if data_request.assigned_to:
            _add_audit_event(db, data_request.id, "assigned", "Request assigned.", {"assigned_to": data_request.assigned_to})
        if data_request.due_date:
            _add_audit_event(
                db,
                data_request.id,
                "due_date_changed",
                "Due date set.",
                {"due_date": data_request.due_date.isoformat()},
            )
        if data_request.status == "completed":
            _add_audit_event(db, data_request.id, "completed", "Request marked completed.")

    note_request = created_requests[1]
    db.add(
        models.DataRequestNote(
            data_request_id=note_request.id,
            note="Demo note: verification is in progress before deletion is completed.",
            created_by="demo-admin",
        )
    )
    _add_audit_event(db, note_request.id, "note_added", "Demo note added.", {"created_by": "demo-admin"})


def _add_audit_event(
    db: Session,
    data_request_id: Any,
    event_type: str,
    message: str,
    metadata: dict[str, object] | None = None,
) -> None:
    db.add(
        models.DataRequestAuditEvent(
            data_request_id=data_request_id,
            event_type=event_type,
            message=message,
            event_metadata=metadata,
        )
    )


def _replace_demo_consent_events(db: Session, project: models.Project) -> None:
    existing = list(
        db.scalars(
            select(models.ConsentEvent).where(
                models.ConsentEvent.project_id == project.id,
                models.ConsentEvent.external_user_id.in_(DEMO_USER_IDS),
            )
        ).all()
    )
    for event in existing:
        db.delete(event)
    db.flush()

    events = [
        {
            "external_user_id": "usr_demo_001",
            "purpose": "marketing_whatsapp",
            "status": "granted",
            "notice_version": "v2.1",
            "source": "web_signup",
            "occurred_at": datetime(2026, 4, 10, 10, 0, tzinfo=timezone.utc),
            "event_metadata": {"ip_country": "IN", "ui_surface": "signup_checkbox"},
        },
        {
            "external_user_id": "usr_demo_001",
            "purpose": "marketing_whatsapp",
            "status": "withdrawn",
            "notice_version": "v2.1",
            "source": "account_settings",
            "occurred_at": datetime(2026, 4, 20, 14, 30, tzinfo=timezone.utc),
            "event_metadata": {"ui_surface": "preferences_page"},
        },
        {
            "external_user_id": "usr_demo_002",
            "purpose": "ai_processing",
            "status": "granted",
            "notice_version": "v2.1",
            "source": "mobile_app",
            "occurred_at": datetime(2026, 4, 21, 9, 15, tzinfo=timezone.utc),
            "event_metadata": {"ui_surface": "ai_tutor_consent"},
        },
        {
            "external_user_id": "usr_demo_003",
            "purpose": "product_analytics",
            "status": "granted",
            "notice_version": "v2.1",
            "source": "web_signup",
            "occurred_at": datetime(2026, 4, 22, 11, 45, tzinfo=timezone.utc),
            "event_metadata": {"ui_surface": "signup_checkbox"},
        },
    ]
    for item in events:
        db.add(models.ConsentEvent(project_id=project.id, **item))


if __name__ == "__main__":
    main()
