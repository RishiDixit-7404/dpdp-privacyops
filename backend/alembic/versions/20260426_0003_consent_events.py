"""add consent event ledger

Revision ID: 20260426_0003
Revises: 20260426_0002
Create Date: 2026-04-26 00:00:00.000000+00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260426_0003"
down_revision: Union[str, None] = "20260426_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "consent_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("external_user_id", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("notice_version", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(trim(external_user_id)) > 0", name="ck_consent_events_external_user_id_not_empty"),
        sa.CheckConstraint("length(trim(notice_version)) > 0", name="ck_consent_events_notice_version_not_empty"),
        sa.CheckConstraint("length(trim(purpose)) > 0", name="ck_consent_events_purpose_not_empty"),
        sa.CheckConstraint("status in ('granted', 'withdrawn')", name="ck_consent_events_status"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_consent_events_project_id"), "consent_events", ["project_id"], unique=False)
    op.create_index(op.f("ix_consent_events_external_user_id"), "consent_events", ["external_user_id"], unique=False)
    op.create_index(op.f("ix_consent_events_purpose"), "consent_events", ["purpose"], unique=False)
    op.create_index(op.f("ix_consent_events_status"), "consent_events", ["status"], unique=False)
    op.create_index(op.f("ix_consent_events_occurred_at"), "consent_events", ["occurred_at"], unique=False)
    op.create_index(
        "ix_consent_events_project_user_purpose_occurred",
        "consent_events",
        ["project_id", "external_user_id", "purpose", "occurred_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_consent_events_project_user_purpose_occurred", table_name="consent_events")
    op.drop_index(op.f("ix_consent_events_occurred_at"), table_name="consent_events")
    op.drop_index(op.f("ix_consent_events_status"), table_name="consent_events")
    op.drop_index(op.f("ix_consent_events_purpose"), table_name="consent_events")
    op.drop_index(op.f("ix_consent_events_external_user_id"), table_name="consent_events")
    op.drop_index(op.f("ix_consent_events_project_id"), table_name="consent_events")
    op.drop_table("consent_events")
