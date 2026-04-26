"""add data request inbox tables

Revision ID: 20260426_0002
Revises: 20260426_0001
Create Date: 2026-04-26 00:00:00.000000+00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260426_0002"
down_revision: Union[str, None] = "20260426_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("request_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("requester_name", sa.String(length=255), nullable=True),
        sa.Column("requester_email", sa.String(length=320), nullable=False),
        sa.Column("requester_identifier", sa.String(length=255), nullable=True),
        sa.Column("request_details", sa.Text(), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assigned_to", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "request_type in ('access', 'correction', 'deletion', 'consent_withdrawal', 'grievance')",
            name="ck_data_requests_request_type",
        ),
        sa.CheckConstraint(
            "status in ('new', 'verifying', 'in_progress', 'completed', 'rejected')",
            name="ck_data_requests_status",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_data_requests_project_id"), "data_requests", ["project_id"], unique=False)
    op.create_index(op.f("ix_data_requests_request_type"), "data_requests", ["request_type"], unique=False)
    op.create_index(op.f("ix_data_requests_status"), "data_requests", ["status"], unique=False)
    op.create_index(op.f("ix_data_requests_requester_email"), "data_requests", ["requester_email"], unique=False)

    op.create_table(
        "data_request_notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("data_request_id", sa.Uuid(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_request_id"], ["data_requests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_data_request_notes_data_request_id"), "data_request_notes", ["data_request_id"], unique=False)

    op.create_table(
        "data_request_audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("data_request_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "event_type in ('created', 'status_changed', 'note_added', 'assigned', 'due_date_changed', 'completed', 'rejected')",
            name="ck_data_request_audit_events_event_type",
        ),
        sa.ForeignKeyConstraint(["data_request_id"], ["data_requests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_data_request_audit_events_data_request_id"),
        "data_request_audit_events",
        ["data_request_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_data_request_audit_events_event_type"),
        "data_request_audit_events",
        ["event_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_data_request_audit_events_event_type"), table_name="data_request_audit_events")
    op.drop_index(op.f("ix_data_request_audit_events_data_request_id"), table_name="data_request_audit_events")
    op.drop_table("data_request_audit_events")
    op.drop_index(op.f("ix_data_request_notes_data_request_id"), table_name="data_request_notes")
    op.drop_table("data_request_notes")
    op.drop_index(op.f("ix_data_requests_requester_email"), table_name="data_requests")
    op.drop_index(op.f("ix_data_requests_status"), table_name="data_requests")
    op.drop_index(op.f("ix_data_requests_request_type"), table_name="data_requests")
    op.drop_index(op.f("ix_data_requests_project_id"), table_name="data_requests")
    op.drop_table("data_requests")
